from json import dumps
from os import environ
from typing import Dict, List, Union

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from change_event_exceptions import ValidationException
from change_event_validation import validate_event
from change_request import ChangeRequest
from changes import get_changes
from common.dynamodb import add_change_request_to_dynamodb
from common.middlewares import set_correlation_id, unhandled_exception_logging
from common.utilities import extract_body, get_sequence_number, invoke_lambda_function, is_mock_mode
from dos import VALID_SERVICE_TYPES, VALID_STATUS_ID, DoSService, get_matching_dos_services
from nhs import NHSEntity
from reporting import log_unmatched_nhsuk_pharmacies, report_closed_or_hidden_services

logger = Logger()
tracer = Tracer()

EXPECTED_ENVIRONMENT_VARIABLES = (
    "DB_SERVER",
    "DB_PORT",
    "DB_NAME",
    "DB_SCHEMA",
    "DB_USER_NAME",
    "EVENT_SENDER_LAMBDA_NAME",
)


class EventProcessor:
    matching_services = None
    change_requests = None

    def __init__(self, nhs_entity: NHSEntity):
        self.nhs_entity = nhs_entity

    def get_matching_services(self) -> List[DoSService]:
        """Using the nhs entity attributed to this object, it finds the
        matching DoS services from the db and filters the results
        """

        # Check database for services with same first 5 digits of ODSCode
        matching_services = get_matching_dos_services(self.nhs_entity.odscode)
        logger.info(
            f"Found {len(matching_services)} services in DB with "
            f"matching first 5 chars of ODSCode: {matching_services}"
        )

        # Filter for services with valid type and status
        matching_services = [
            s for s in matching_services if int(s.typeid) in VALID_SERVICE_TYPES and int(s.statusid) == VALID_STATUS_ID
        ]

        logger.info(
            f"Found {len(matching_services)} services with typeid in "
            f"whitelist{VALID_SERVICE_TYPES} and status id = "
            f"{VALID_STATUS_ID}: {matching_services}"
        )

        self.matching_services = matching_services
        return self.matching_services

    def get_change_requests(self) -> Union[Dict[str, str], None]:
        """Generates change requests needed for the found services to make them inline with the NHS Entity

        Returns:
            Union[Dict[str, str], None]: A dictionary of change requests or none
        """
        if self.matching_services is None:
            logger.error("Attempting to form change requests before matching services have been found.")
            return None

        change_requests = []
        for service in self.matching_services:

            # Find changes, don't make a change req if none found
            changes = get_changes(service, self.nhs_entity)
            logger.info(f"Changes for nhs:{self.nhs_entity.odscode}/dos:{service.id} : {changes}")
            if len(changes) > 0:
                change_requests.append(ChangeRequest(service.id, changes))

        payload_list = dumps([cr.create_payload() for cr in change_requests], default=str)
        logger.info(f"Created {len(change_requests)} change requests {payload_list}")

        # Assign to attribute and return
        self.change_requests = change_requests
        return self.change_requests

    def send_changes(self) -> None:
        """Sends change request payload off to next part of workflow
        [Which at the moment is straight to the next lambda]
        """
        if self.change_requests is None:
            logger.error("Attempting to send change requests before get_change_requests has been called.")
            return

        if "EVENT_SENDER_LAMBDA_NAME" not in environ:
            logger.error("Attempting to send change requests but EVENT_SENDER_LAMBDA_NAME is not set.")
            return

        for change_request in self.change_requests:
            change_payload = change_request.create_payload()
            invoke_lambda_function(environ["EVENT_SENDER_LAMBDA_NAME"], change_payload)
            logger.info(f"Sent off change payload for id={change_request.service_id}")


@unhandled_exception_logging()
@tracer.capture_lambda_handler()
@event_source(data_class=SQSEvent)
@set_correlation_id()
@logger.inject_lambda_context()
def lambda_handler(event: SQSEvent, context: LambdaContext) -> None:
    """Entrypoint handler for the event_processor lambda

    Args:
        event (SQSEvent): Lambda function invocation event (list of 1 SQS Message)
        context (LambdaContext): Lambda function context object

    Event: The event payload should contain a NHS Entity (Service)

    Some code may need to be changed if the exact input format is changed.
    """
    for env_var in EXPECTED_ENVIRONMENT_VARIABLES:
        if env_var not in environ:
            logger.error(f"Environmental variable {env_var} not present")
            return

    counter = 0
    for record in event.records:
        counter += 1
        if counter > 1:
            logger.error("More than one record found in event", extra={"event": event})
            return

    record = next(event.records)
    message = record.body

    sequence_number = get_sequence_number(record)
    change_event = extract_body(message)
    sqs_timestamp = str(record.attributes["SentTimestamp"])
    # Save Event to dynamo so can be retrieved later
    add_change_request_to_dynamodb(change_event, sequence_number, sqs_timestamp)
    logger.info(f"Attempting to validate change_event: {change_event}")
    if sequence_number is None:
        logger.error("No sequence number provided, so message will be ignored")
        return
    nhs_entity = NHSEntity(change_event)
    logger.append_keys(ods_code=nhs_entity.odscode)
    logger.append_keys(org_type=nhs_entity.org_type)
    logger.append_keys(org_sub_type=nhs_entity.org_sub_type)
    logger.info("Begun event processor function", extra={"nhs_entity": nhs_entity})

    try:
        validate_event(change_event)
    except ValidationException:
        return

    event_processor = EventProcessor(nhs_entity)
    logger.info("Getting matching DoS Services")
    matching_services = event_processor.get_matching_services()

    if len(matching_services) == 0:
        log_unmatched_nhsuk_pharmacies(nhs_entity)
        return

    if nhs_entity.is_status_hidden_or_closed():
        report_closed_or_hidden_services(nhs_entity, matching_services)
        return

    event_processor.get_change_requests()
    disconnect_dos_db()

    if not is_mock_mode():
        event_processor.send_changes()
    else:
        logger.info("Mock Mode on. Change requests will not be sent")

    