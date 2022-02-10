from json import dumps
from os import environ, getenv
from typing import Dict, List, Union
from boto3 import client
from base64 import b64encode
from time import strftime, gmtime, time_ns, time
from aws_embedded_metrics import metric_scope
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from change_event_exceptions import ValidationException
from change_event_validation import validate_event
from change_request import ChangeRequest
from changes import get_changes
from common.dynamodb import add_change_request_to_dynamodb, get_latest_sequence_id_for_a_given_odscode_from_dynamodb
from common.middlewares import set_correlation_id, unhandled_exception_logging
from common.utilities import extract_body, get_sequence_number
from common.dos import VALID_SERVICE_TYPES, VALID_STATUS_ID, DoSService, get_matching_dos_services, disconnect_dos_db
from nhs import NHSEntity
from reporting import log_invalid_open_times, log_unmatched_nhsuk_pharmacies, report_closed_or_hidden_services
from common.encryption import initialise_encryption_client


logger = Logger()
tracer = Tracer()
EXPECTED_ENVIRONMENT_VARIABLES = (
    "DB_SERVER",
    "DB_PORT",
    "DB_NAME",
    "DB_SCHEMA",
    "DB_USER_NAME",
    "EVENTBRIDGE_BUS_NAME",
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
        logger.info(f"Getting matching DoS Services for odscode '{self.nhs_entity.odscode}'.")
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
            Union[Dict[str, str], None]: A dictionary of change requests or none.
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

    def send_changes(self, message_received: int, record_id: str) -> None:
        """Sends change request payload off to next part of workflow
        [Which at the moment is straight to the next lambda]
        """
        if self.change_requests is None:
            logger.error("Attempting to send change requests before get_change_requests has been called.")
            return

        key_data = {
            "message_received": message_received,
            "dynamo_record_id": record_id,
            "ods_code": self.nhs_entity.odscode,
            "time": time(),
        }
        logger.info("Getting Encryption Client")
        encryption_helper = initialise_encryption_client()
        logger.info("Getting signing key")
        signing_key = encryption_helper.encrypt_string(dumps(key_data))
        b64_mystring = b64encode(signing_key).decode("utf-8")
        logger.debug(f"signing key : {b64_mystring}")
        eventbridge = client("events")
        events = []
        for change_request in self.change_requests:
            change_payload = change_request.create_payload()
            events.append(
                {
                    "Source": "event-processor",
                    "DetailType": "change-request",
                    "Detail": dumps(
                        {
                            "signing_key": b64_mystring,
                            "change_payload": change_payload,
                            "correlation_id": logger.get_correlation_id(),
                            "message_received": message_received,
                            "dynamo_record_id": record_id,
                            "ods_code": self.nhs_entity.odscode,
                        }
                    ),
                    "EventBusName": getenv("EVENTBRIDGE_BUS_NAME"),
                }
            )
        if len(events) > 0:
            response = eventbridge.put_events(Entries=events)
            logger.info("Response from eventbridge put_events", extra={"response": response})
            logger.info(f"Sent off change payload for id={change_request.service_id}")
        else:
            logger.info("No changes identified")


@unhandled_exception_logging()
@tracer.capture_lambda_handler()
@event_source(data_class=SQSEvent)
@set_correlation_id()
@logger.inject_lambda_context
@metric_scope
def lambda_handler(event: SQSEvent, context: LambdaContext, metrics) -> None:
    """Entrypoint handler for the event_processor lambda

    Args:
        event (SQSEvent): Lambda function invocation event (list of 1 SQS Message)
        context (LambdaContext): Lambda function context object

    Event: The event payload should contain a NHS Entity (Service)

    Some code may need to be changed if the exact input format is changed.
    """

    now_ms = time_ns() // 1000000
    logger.append_keys(ods_code=None)
    logger.append_keys(org_type=None)
    logger.append_keys(org_sub_type=None)
    logger.append_keys(dynamo_record_id=None)
    logger.append_keys(message_received=None)
    for env_var in EXPECTED_ENVIRONMENT_VARIABLES:
        if env_var not in environ:
            logger.error(f"Environmental variable {env_var} not present")
            return

    if len(list(event.records)) != 1:
        raise Exception(f"{len(list(event.records))} records found in event. Expected 1.")

    record = next(event.records)
    message = record.body
    change_event = extract_body(message)
    sequence_number = get_sequence_number(record)
    sqs_timestamp = int(record.attributes["SentTimestamp"])

    s, ms = divmod(sqs_timestamp, 1000)
    message_received_pretty = "%s.%03d" % (strftime("%Y-%m-%d %H:%M:%S", gmtime(s)), ms)
    logger.append_keys(message_received=message_received_pretty)
    logger.info("Change Event received", extra={"event": event})
    metrics.set_namespace("UEC-DOS-INT")
    metrics.set_property("level", "INFO")
    metrics.set_property("function_name", context.function_name)
    metrics.set_property("message_received", message_received_pretty)
    logger.info("Getting latest sequence number")
    db_latest_sequence_number = get_latest_sequence_id_for_a_given_odscode_from_dynamodb(change_event["ODSCode"])
    logger.info("Writing change event to dynamo")
    record_id = add_change_request_to_dynamodb(change_event, sequence_number, sqs_timestamp)

    metrics.set_property("correlation_id", logger.get_correlation_id())
    metrics.set_property("dynamo_record_id", record_id)
    metrics.set_dimensions({"ENV": environ["ENV"]})
    metrics.put_metric("QueueToProcessorLatency", now_ms - sqs_timestamp, "Milliseconds")
    logger.append_keys(dynamo_record_id=record_id)
    if sequence_number is None:
        logger.error("No sequence number provided, so message will be ignored.")
        return
    elif sequence_number < db_latest_sequence_number:
        logger.error("Sequence id is smaller than the existing one in db for a given odscode, so will be ignored")
        return

    try:
        validate_event(change_event)

        nhs_entity = NHSEntity(change_event)
        logger.append_keys(ods_code=nhs_entity.odscode)
        logger.append_keys(org_type=nhs_entity.org_type)
        logger.append_keys(org_sub_type=nhs_entity.org_sub_type)
        metrics.set_property("ods_code", nhs_entity.odscode)
        logger.info("Created NHS Entity for processing", extra={"nhs_entity": nhs_entity})
        event_processor = EventProcessor(nhs_entity)
        matching_services = event_processor.get_matching_services()
        if len(matching_services) == 0:
            log_unmatched_nhsuk_pharmacies(nhs_entity)
            return

        if nhs_entity.is_status_hidden_or_closed():
            report_closed_or_hidden_services(nhs_entity, matching_services)
            return

        if not nhs_entity.all_times_valid():
            log_invalid_open_times(nhs_entity, matching_services)

        event_processor.get_change_requests()

    except ValidationException as err:
        logger.exception("Something went wrong", extra={"error": err})
        raise
    finally:
        disconnect_dos_db()

    event_processor.send_changes(sqs_timestamp, record_id)
