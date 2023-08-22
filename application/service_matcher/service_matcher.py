from ast import literal_eval
from datetime import datetime
from hashlib import sha256
from json import dumps
from operator import countOf
from os import environ, getenv
from typing import Any

from aws_embedded_metrics import metric_scope
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.tracing import Tracer
from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from boto3 import client
from pytz import timezone

from .reporting import (
    log_closed_or_hidden_services,
    log_invalid_open_times,
    log_unexpected_pharmacy_profiling,
    log_unmatched_nhsuk_service,
)
from common.constants import BLOOD_PRESSURE, CONTRACEPTION, PHARMACY_SERVICE_TYPE_ID
from common.dos import ACTIVE_STATUS_ID, DoSService, get_matching_dos_services
from common.middlewares import unhandled_exception_logging
from common.nhs import NHSEntity
from common.types import HoldingQueueChangeEventItem, UpdateRequest
from common.utilities import extract_body

logger = Logger()
tracer = Tracer()
sqs = client("sqs")


@unhandled_exception_logging()
@tracer.capture_lambda_handler()
@logger.inject_lambda_context(clear_state=True)
@event_source(data_class=SQSEvent)
@metric_scope
def lambda_handler(event: SQSEvent, context: LambdaContext, metrics: Any) -> None:  # noqa: ANN401
    """Entrypoint handler for the service_matcher lambda.

    Args:
        event (SQSEvent): Lambda function invocation event (list of 1 SQS Message)
            Change Event has been validate by the ingest change event lambda
        context (LambdaContext): Lambda function context object
        metrics (Any): Embedded metrics object

    Event: The event payload should contain a NHS Entity (Service)
    """
    record = next(event.records)
    holding_queue_change_event_item: HoldingQueueChangeEventItem = extract_body(record.body)
    logger.set_correlation_id(holding_queue_change_event_item["correlation_id"])
    change_event = holding_queue_change_event_item["change_event"]

    metrics.set_namespace("UEC-DOS-INT")
    metrics.set_property("level", "INFO")
    metrics.set_property("function_name", context.function_name)

    # Get Datetime from milliseconds
    date_time = datetime.fromtimestamp(
        holding_queue_change_event_item["message_received"] // 1000.0,
        tz=timezone("Europe/London"),
    )
    metrics.set_property("message_received", date_time.strftime("%m/%d/%Y, %H:%M:%S"))

    nhs_entity = NHSEntity(change_event)
    logger.append_keys(ods_code=nhs_entity.odscode)
    logger.append_keys(org_type=nhs_entity.org_type)
    logger.append_keys(org_sub_type=nhs_entity.org_sub_type)
    metrics.set_property("ods_code", nhs_entity.odscode)
    logger.info("Created NHS Entity for processing", extra={"nhs_entity": nhs_entity})
    matching_services = get_matching_services(nhs_entity)

    if len(matching_services) == 0 or not next(
        (True for service in matching_services if service.statusid == ACTIVE_STATUS_ID), False,
    ):
        log_unmatched_nhsuk_service(nhs_entity)
        return

    if nhs_entity.is_status_hidden_or_closed():
        log_closed_or_hidden_services(nhs_entity, matching_services)
        return

    if not nhs_entity.all_times_valid():
        log_invalid_open_times(nhs_entity, matching_services)

    # Check for correct pharmacy profiling
    dos_matching_service_types = [service.typeid for service in matching_services]
    logger.debug(f"Matching service types: {dos_matching_service_types}")
    if countOf(dos_matching_service_types, PHARMACY_SERVICE_TYPE_ID) > 1:
        type_13_matching_services = [
            service for service in matching_services if service.typeid == PHARMACY_SERVICE_TYPE_ID
        ]
        log_unexpected_pharmacy_profiling(
            nhs_entity=nhs_entity,
            matching_services=type_13_matching_services,
            reason="Multiple 'Pharmacy' type services found (type 13)",
        )
    elif countOf(dos_matching_service_types, PHARMACY_SERVICE_TYPE_ID) == 0:
        log_unexpected_pharmacy_profiling(
            nhs_entity=nhs_entity,
            matching_services=matching_services,
            reason="No 'Pharmacy' type services found (type 13)",
        )

    log_missing_dos_profiling(nhs_entity, matching_services, BLOOD_PRESSURE)
    log_missing_dos_profiling(nhs_entity, matching_services, CONTRACEPTION)

    update_requests: list[UpdateRequest] = [
        {"change_event": change_event, "service_id": str(dos_service.id)} for dos_service in matching_services
    ]

    send_update_requests(
        update_requests=update_requests,
        message_received=holding_queue_change_event_item["message_received"],
        record_id=holding_queue_change_event_item["dynamo_record_id"],
        sequence_number=holding_queue_change_event_item["sequence_number"],
    )

def log_missing_dos_profiling(nhs_entity: NHSEntity, matching: list[DoSService], service_const: dict[str,str]) -> None:
    """Reports when a Change Event has a Service Code defined and there isn't a corresponding DoS service.

    Args:
        nhs_entity (NHSEntity): The nhs entity to check for the service
        matching (List[DosService]): The matching DoS service to check for the
        service_const (dict[str, str]): Dictionary of service constants to identify the service
    """
    if (nhs_entity.check_for_service(service_const["nhs_uk_service_code"])
        and not next((True for service in matching if service.typeid == service_const["dos_type_id"]), False)):
        log_unexpected_pharmacy_profiling(
            nhs_entity=nhs_entity,
            matching_services=matching,
            reason= f"""No '{service_const['name']}' type services found in DoS even though its specified
            in the NHS UK Change Event (dos type {service_const['dos_type_id']} )""",
        )


def divide_chunks(to_chunk: list, chunk_size: int) -> Any:  # noqa: ANN401
    """Yield successive n-sized chunks from l."""
    # looping till length l
    for i in range(0, len(to_chunk), chunk_size):
        yield to_chunk[i : i + chunk_size]


def get_matching_services(nhs_entity: NHSEntity) -> list[DoSService]:
    """Gets the matching DoS services for the given nhs entity.

    Using the nhs entity attributed to this object, it finds the
    matching DoS services from the db and filters the results.

    Args:
        nhs_entity (NHSEntity): The nhs entity to match against.

    Returns:
        list[DoSService]: The list of matching DoS services.
    """
    # Check database for services with same first 5 digits of ODSCode
    logger.info(f"Getting matching DoS Services for odscode '{nhs_entity.odscode}'.")
    pharmacy_first_phase_one_feature_flag = get_pharmacy_first_phase_one_feature_flag()
    matching_services = get_matching_dos_services(nhs_entity.odscode, pharmacy_first_phase_one_feature_flag)
    logger.info(
        f"Found {len(matching_services)} services in DB with "
        f"matching first 5 chars of ODSCode: {matching_services}",
        extra={"pharmacy_first_phase_one_feature_flag": pharmacy_first_phase_one_feature_flag},
    )

    return matching_services


def get_pharmacy_first_phase_one_feature_flag() -> bool:
    """Gets the pharmacy first phase one feature flag.

    Returns:
        bool: True if the feature flag is enabled, False otherwise.
    """
    parameter_name: str = getenv("PHARMACY_FIRST_PHASE_ONE_PARAMETER")
    pharmacy_first_phase_one: str = parameters.get_parameter(parameter_name)
    pharmacy_first_phase_one_feature_flag = literal_eval(pharmacy_first_phase_one)
    logger.debug(
        "Got pharmacy first phase one feature flag",
        extra={"pharmacy_first_phase_one_feature_flag": pharmacy_first_phase_one_feature_flag},
    )
    return pharmacy_first_phase_one_feature_flag


def send_update_requests(
    update_requests: list[dict[str, Any]],
    message_received: int,
    record_id: str,
    sequence_number: int,
) -> None:
    """Sends update request payload off to next part of workflow."""
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
            },
        )
    chunks = list(divide_chunks(messages, 10))
    for i, chunk in enumerate(chunks):
        # TODO: Handle errors?
        logger.debug(f"Sending off message chunk {i+1}/{len(chunks)}")
        response = sqs.send_message_batch(QueueUrl=environ["UPDATE_REQUEST_QUEUE_URL"], Entries=chunk)
        logger.info("Response received", extra={"response": response})
        logger.info(f"Sent off update request for id={service_id}")
