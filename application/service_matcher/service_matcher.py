from hashlib import sha256
from json import dumps
from os import environ, getenv
from typing import Any

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.tracing import Tracer
from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from boto3 import client

from .matching import get_matching_services
from .review_matches import review_matches
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
def lambda_handler(event: SQSEvent, context: LambdaContext) -> None:  # noqa: ARG001
    """Entrypoint handler for the service_matcher lambda.

    Args:
        event (SQSEvent): Lambda function invocation event (list of 1 SQS Message)
            Change Event has been validate by the ingest change event lambda
        context (LambdaContext): Lambda function context object

    Event: The event payload should contain a NHS Entity (Service)
    """
    record = next(event.records)
    holding_queue_change_event_item: HoldingQueueChangeEventItem = extract_body(record.body)
    logger.set_correlation_id(holding_queue_change_event_item["correlation_id"])
    change_event = holding_queue_change_event_item["change_event"]

    nhs_entity = NHSEntity(change_event)
    logger.append_keys(ods_code=nhs_entity.odscode, org_type=nhs_entity.org_type, org_sub_type=nhs_entity.org_sub_type)
    logger.info("Created NHS Entity for processing", nhs_entity=nhs_entity)

    matching_services = get_matching_services(nhs_entity)
    matching_services = review_matches(matching_services, nhs_entity)
    if matching_services is None:
        return
    update_requests: list[UpdateRequest] = [
        {"change_event": change_event, "service_id": str(dos_service.id)} for dos_service in matching_services
    ]

    send_update_requests(
        update_requests=update_requests,
        message_received=holding_queue_change_event_item["message_received"],
        record_id=holding_queue_change_event_item["dynamo_record_id"],
        sequence_number=holding_queue_change_event_item["sequence_number"],
    )


def divide_chunks(to_chunk: list, chunk_size: int) -> Any:  # noqa: ANN401
    """Yield successive n-sized chunks from l."""
    # looping till length l
    for i in range(0, len(to_chunk), chunk_size):
        yield to_chunk[i : i + chunk_size]


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
            update_request=update_request,
            entry_id=entry_id,
            hashed_payload=f"{len(hashed_payload)} - {hashed_payload}",
            message_deduplication_id=message_deduplication_id,
            message_group_id=message_group_id,
            sequence_number=str(sequence_number),
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
        logger.debug("Sent off message chunk", response=response)
        logger.warning(
            "Sent Off Update Request",
            service_id=service_id,
            environment=getenv("ENVIRONMENT"),
            cloudwatch_metric_filter_matching_attribute="UpdateRequestSent",
        )
