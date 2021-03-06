import hashlib
from json import dumps
from os import environ
from time import gmtime, strftime, time_ns
from typing import Dict, List, Union

from aws_embedded_metrics import metric_scope
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from boto3 import client

from change_event_validation import validate_event
from change_request import ChangeRequest
from changes import get_changes
from common.constants import DENTIST_ORG_TYPE_ID, PHARMACY_ORG_TYPE_ID
from common.dos import VALID_STATUS_ID, DoSService, get_matching_dos_services
from common.dos_db_connection import disconnect_dos_db
from common.dynamodb import add_change_request_to_dynamodb, get_latest_sequence_id_for_a_given_odscode_from_dynamodb
from common.middlewares import set_correlation_id, unhandled_exception_logging
from common.service_type import get_valid_service_types
from common.utilities import extract_body, get_sequence_number, remove_given_keys_from_dict_by_msg_limit
from common.nhs import NHSEntity
from reporting import (
    log_closed_or_hidden_services,
    log_invalid_open_times,
    log_service_with_generic_bank_holiday,
    log_unmatched_nhsuk_service,
    log_unmatched_service_types,
)

logger = Logger()
tracer = Tracer()
EXPECTED_ENVIRONMENT_VARIABLES = (
    "DB_SERVER",
    "DB_PORT",
    "DB_NAME",
    "DB_SCHEMA",
    "DB_USER_NAME",
)


def divide_chunks(to_chunk, chunk_size):

    # looping till length l
    for i in range(0, len(to_chunk), chunk_size):
        yield to_chunk[i : i + chunk_size]  # noqa: E203


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
        matching_dos_services = get_matching_dos_services(self.nhs_entity.odscode, self.nhs_entity.org_type_id)

        # Filter for matched and unmatched service types and valid status
        matching_services, non_matching_services = [], []
        valid_service_types = get_valid_service_types(self.nhs_entity.org_type_id)
        for service in matching_dos_services:
            if int(service.statusid) == VALID_STATUS_ID:
                if int(service.typeid) in valid_service_types:
                    matching_services.append(service)
                else:
                    non_matching_services.append(service)
        if len(non_matching_services) > 0:
            log_unmatched_service_types(self.nhs_entity, non_matching_services)

        if self.nhs_entity.org_type_id == PHARMACY_ORG_TYPE_ID:
            logger.info(
                f"Found {len(matching_dos_services)} services in DB with "
                f"matching first 5 chars of ODSCode: {matching_dos_services}"
            )
        elif self.nhs_entity.org_type_id == DENTIST_ORG_TYPE_ID:
            logger.info(
                f"Found {len(matching_dos_services)} services in DB with matching ODSCode: {matching_dos_services}"
            )
        logger.info(
            f"Found {len(matching_services)} services with typeid in "
            f"allowlist {valid_service_types} and status id = "
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
                change_request = ChangeRequest(service.id, changes)
                logger.info("Change Request Created", extra={"change_request": change_request})
                change_requests.append(change_request)

        payload_list = dumps([cr.create_payload() for cr in change_requests], default=str)
        logger.info(f"Created {len(change_requests)} change requests {payload_list}")

        # Assign to attribute and return
        self.change_requests = change_requests
        return self.change_requests

    def send_changes(self, message_received: int, record_id: str, sequence_number: int) -> None:
        """Sends change request payload off to next part of workflow"""
        if self.change_requests is None:
            logger.error("Attempting to send change requests before get_change_requests has been called.")
            return

        sqs = client("sqs")
        messages = []
        for change_request in self.change_requests:
            change_payload = dumps(change_request.create_payload())
            encoded = change_payload.encode()
            hashed_payload = hashlib.sha256(encoded).hexdigest()
            message_deduplication_id = f"{sequence_number}-{hashed_payload}"
            message_group_id = change_request.service_id
            entry_id = f"{change_request.service_id}-{sequence_number}"
            logger.debug(
                "CR to send",
                extra={
                    "change_request": change_payload,
                    "entry_id": entry_id,
                    "hashed_payload": f"{len(hashed_payload)} - {hashed_payload}",
                    "message_deduplication_id": message_deduplication_id,
                    "message_group_id": message_group_id,
                    "sequence_number": str(sequence_number),
                },
            )

            messages.append(
                {
                    "Id": entry_id,
                    "MessageBody": change_payload,
                    "MessageDeduplicationId": message_deduplication_id,
                    "MessageGroupId": message_group_id,
                    "MessageAttributes": {
                        "correlation_id": {"DataType": "String", "StringValue": logger.get_correlation_id()},
                        "message_received": {"DataType": "Number", "StringValue": str(message_received)},
                        "dynamo_record_id": {"DataType": "String", "StringValue": record_id},
                        "ods_code": {"DataType": "String", "StringValue": self.nhs_entity.odscode},
                        "message_deduplication_id": {"DataType": "String", "StringValue": message_deduplication_id},
                        "message_group_id": {"DataType": "String", "StringValue": message_group_id},
                    },
                }
            )
        if len(messages) > 0:
            chunks = list(divide_chunks(messages, 10))
            for i, chunk in enumerate(chunks):
                # TODO: Handle errors?
                logger.debug(f"Sending off message chunk {i+1}/{len(chunks)}")
                response = sqs.send_message_batch(QueueUrl=environ["CR_QUEUE_URL"], Entries=chunk)
                logger.info("Response received", extra={"response": response})
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
    time_start_ns = time_ns()

    logger.append_keys(
        ods_code=None,
        org_type=None,
        org_sub_type=None,
        dynamo_record_id=None,
        message_received=None,
        service_type=None
    )

    for env_var in EXPECTED_ENVIRONMENT_VARIABLES:
        if env_var not in environ:
            logger.error(f"Environmental variable {env_var} not present")
            return

    if len(list(event.records)) != 1:
        raise Exception(f"{len(list(event.records))} records found in event. Expected 1.")

    record = next(event.records)
    change_event = extract_body(record.body)
    ods_code = change_event.get("ODSCode")
    logger.append_keys(ods_code=ods_code)
    sequence_number = get_sequence_number(record)
    sqs_timestamp = int(record.attributes["SentTimestamp"])
    s, ms = divmod(sqs_timestamp, 1000)
    message_received_pretty = "%s.%03d" % (strftime("%Y-%m-%d %H:%M:%S", gmtime(s)), ms)
    logger.append_keys(message_received=message_received_pretty)
    change_event_for_log = remove_given_keys_from_dict_by_msg_limit(change_event, ["Facilities", "Metrics"], 10000)
    logger.info("Change Event received", extra={"change-event": change_event_for_log})
    metrics.set_namespace("UEC-DOS-INT")
    metrics.set_property("level", "INFO")
    metrics.set_property("function_name", context.function_name)
    metrics.set_property("message_received", message_received_pretty)

    logger.info("Getting latest sequence number")
    db_latest_sequence_number = get_latest_sequence_id_for_a_given_odscode_from_dynamodb(ods_code)
    logger.info("Writing change event to dynamo")
    record_id = add_change_request_to_dynamodb(change_event, sequence_number, sqs_timestamp)
    correlation_id = logger.get_correlation_id()
    if "broken" in correlation_id.lower():
        raise ValueError("Everything is broken boo")
    metrics.set_property("correlation_id", logger.get_correlation_id())
    metrics.set_property("dynamo_record_id", record_id)
    metrics.set_dimensions({"ENV": environ["ENV"]})
    metrics.put_metric("QueueToProcessorLatency", (time_start_ns // 1000000) - sqs_timestamp, "Milliseconds")
    logger.append_keys(dynamo_record_id=record_id)

    if sequence_number is None:
        logger.error("No sequence number provided, so message will be ignored.")
        return
    elif sequence_number < db_latest_sequence_number:
        logger.error(
            "Sequence id is smaller than the existing one in db for a given odscode, so will be ignored",
            extra={"incoming_sequence_number": sequence_number, "db_latest_sequence_number": db_latest_sequence_number},
        )
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
            log_unmatched_nhsuk_service(nhs_entity)
            return

        if nhs_entity.is_status_hidden_or_closed():
            log_closed_or_hidden_services(nhs_entity, matching_services)
            return

        if not nhs_entity.all_times_valid():
            log_invalid_open_times(nhs_entity, matching_services)

        for dos_service in matching_services:
            if dos_service.any_generic_bankholiday_open_periods():
                log_service_with_generic_bank_holiday(nhs_entity, dos_service)

        event_processor.get_change_requests()

    finally:
        disconnect_dos_db()

    event_processor.send_changes(sqs_timestamp, record_id, sequence_number)
