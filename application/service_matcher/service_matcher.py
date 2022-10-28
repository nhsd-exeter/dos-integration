from hashlib import sha256
from json import dumps
from os import environ
from time import gmtime, strftime, time_ns
from typing import Any, Dict, List

from aws_embedded_metrics import metric_scope
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.tracing import Tracer
from aws_lambda_powertools.utilities.data_classes import event_source, SQSEvent
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from boto3 import client

from .change_event_validation import validate_change_event
from common.constants import DENTIST_ORG_TYPE_ID, PHARMACY_ORG_TYPE_ID
from common.dos import DoSService, get_matching_dos_services, VALID_STATUS_ID
from common.dynamodb import add_change_event_to_dynamodb, get_latest_sequence_id_for_a_given_odscode_from_dynamodb
from common.middlewares import unhandled_exception_logging
from common.nhs import NHSEntity
from common.report_logging import (
    log_blank_standard_opening_times,
    log_closed_or_hidden_services,
    log_invalid_open_times,
    log_unmatched_nhsuk_service,
    log_unmatched_service_types,
)
from common.service_type import get_valid_service_types
from common.types import UpdateRequest
from common.utilities import extract_body, get_sequence_number, remove_given_keys_from_dict_by_msg_limit

logger = Logger()
tracer = Tracer()


@unhandled_exception_logging()
@tracer.capture_lambda_handler()
@event_source(data_class=SQSEvent)
@logger.inject_lambda_context(
    clear_state=True,
    correlation_id_path='Records[0].messageAttributes."correlation-id".stringValue')
@metric_scope
def lambda_handler(event: SQSEvent, context: LambdaContext, metrics) -> None:
    """Entrypoint handler for the service_matcher lambda

    Args:
        event (SQSEvent): Lambda function invocation event (list of 1 SQS Message)
        context (LambdaContext): Lambda function context object

    Event: The event payload should contain a NHS Entity (Service)

    Some code may need to be changed if the exact input format is changed.
    """
    time_start_ns = time_ns()
    if len(list(event.records)) != 1:
        raise ValueError(f"{len(list(event.records))} records found in event. Expected 1.")

    record = next(event.records)
    change_event = extract_body(record.body)
    ods_code = change_event.get("ODSCode")
    add_change_event_received_metric(ods_code=ods_code)
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
    record_id = add_change_event_to_dynamodb(change_event, sequence_number, sqs_timestamp)
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

    validate_change_event(change_event)
    nhs_entity = NHSEntity(change_event)
    logger.append_keys(ods_code=nhs_entity.odscode)
    logger.append_keys(org_type=nhs_entity.org_type)
    logger.append_keys(org_sub_type=nhs_entity.org_sub_type)
    metrics.set_property("ods_code", nhs_entity.odscode)
    logger.info("Created NHS Entity for processing", extra={"nhs_entity": nhs_entity})
    matching_services = get_matching_services(nhs_entity)

    if len(matching_services) == 0:
        log_unmatched_nhsuk_service(nhs_entity)
        return

    if nhs_entity.is_status_hidden_or_closed():
        log_closed_or_hidden_services(nhs_entity, matching_services)
        return

    if not nhs_entity.all_times_valid():
        log_invalid_open_times(nhs_entity, matching_services)

    if nhs_entity.standard_opening_times.fully_closed() and len(matching_services) > 0:
        # Also requires valid type/subtype, but this condition is already met in code by this point
        log_blank_standard_opening_times(nhs_entity, matching_services)

    update_requests: list[UpdateRequest] = [
        {"change_event": change_event, "service_id": str(dos_service.id)} for dos_service in matching_services
    ]

    send_update_requests(update_requests, sqs_timestamp, record_id, sequence_number)


def divide_chunks(to_chunk, chunk_size):
    # looping till length l
    for i in range(0, len(to_chunk), chunk_size):
        yield to_chunk[i : i + chunk_size]  # noqa: E203


def get_matching_services(nhs_entity: NHSEntity) -> List[DoSService]:
    """Using the nhs entity attributed to this object, it finds the
    matching DoS services from the db and filters the results"""
    # Check database for services with same first 5 digits of ODSCode
    logger.info(f"Getting matching DoS Services for odscode '{nhs_entity.odscode}'.")
    matching_dos_services = get_matching_dos_services(nhs_entity.odscode, nhs_entity.org_type_id)

    # Filter for matched and unmatched service types and valid status
    matching_services, non_matching_services = [], []
    valid_service_types = get_valid_service_types(nhs_entity.org_type_id)
    for service in matching_dos_services:
        if int(service.statusid) == VALID_STATUS_ID:
            if int(service.typeid) in valid_service_types:
                matching_services.append(service)
            else:
                non_matching_services.append(service)
    if len(non_matching_services) > 0:
        log_unmatched_service_types(nhs_entity, non_matching_services)

    if nhs_entity.org_type_id == PHARMACY_ORG_TYPE_ID:
        logger.info(
            f"Found {len(matching_dos_services)} services in DB with "
            f"matching first 5 chars of ODSCode: {matching_dos_services}"
        )
    elif nhs_entity.org_type_id == DENTIST_ORG_TYPE_ID:
        logger.info(f"Found {len(matching_dos_services)} services in DB with matching ODSCode: {matching_dos_services}")
    logger.info(
        f"Found {len(matching_services)} services with typeid in "
        f"allowlist {valid_service_types} and status id = "
        f"{VALID_STATUS_ID}: {matching_services}"
    )

    return matching_services


def send_update_requests(
    update_requests: List[Dict[str, Any]], message_received: int, record_id: str, sequence_number: int
) -> None:
    """Sends update request payload off to next part of workflow"""
    sqs = client("sqs")
    messages = []
    for update_request in update_requests:
        service_id = update_request.get("service_id")
        update_request_json = dumps(update_request)
        encoded = update_request_json.encode()
        hashed_payload = sha256(encoded).hexdigest()
        message_deduplication_id = f"{service_id}-{hashed_payload}"
        message_group_id = str(service_id)
        entry_id = f"{service_id}-{sequence_number}"
        logger.debug(
            "Update request to send",
            extra={
                "update_request": update_request,
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
                "MessageBody": update_request_json,
                "MessageDeduplicationId": message_deduplication_id,
                "MessageGroupId": message_group_id,
                "MessageAttributes": {
                    "correlation_id": {"DataType": "String", "StringValue": logger.get_correlation_id()},
                    "message_received": {"DataType": "Number", "StringValue": str(message_received)},
                    "dynamo_record_id": {"DataType": "String", "StringValue": record_id},
                    "ods_code": {
                        "DataType": "String",
                        "StringValue": update_request.get("change_event").get("ODSCode"),
                    },
                    "message_deduplication_id": {"DataType": "String", "StringValue": message_deduplication_id},
                    "message_group_id": {"DataType": "String", "StringValue": message_group_id},
                },
            }
        )
    chunks = list(divide_chunks(messages, 10))
    for i, chunk in enumerate(chunks):
        # TODO: Handle errors?
        logger.debug(f"Sending off message chunk {i+1}/{len(chunks)}")
        response = sqs.send_message_batch(QueueUrl=environ["UPDATE_REQUEST_QUEUE_URL"], Entries=chunk)
        logger.info("Response received", extra={"response": response})
        logger.info(f"Sent off update request for id={service_id}")


@metric_scope
def add_change_event_received_metric(ods_code: str, metrics) -> None:  # type: ignore
    """Adds a success metric to the custom metrics collection

    Args:
        event (UpdateRequestQueueItem): Lambda function invocation event
    """
    metrics.set_namespace("UEC-DOS-INT")
    metrics.set_property("level", "INFO")
    metrics.set_property("message", f"Change Event Received for ODSCode: {ods_code}")
    metrics.put_metric("ChangeEventReceived", 1, "Count")
    metrics.set_dimensions({"ENV": environ["ENV"]})
