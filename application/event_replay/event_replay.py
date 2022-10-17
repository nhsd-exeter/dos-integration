from decimal import Decimal
from os import getenv
from time import time_ns
from typing import Any, Dict

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.tracing import Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from boto3 import client
from boto3.dynamodb.types import TypeDeserializer
from simplejson import dumps

from common.middlewares import unhandled_exception_logging

tracer = Tracer()
logger = Logger()


@tracer.capture_lambda_handler()
@unhandled_exception_logging
@logger.inject_lambda_context
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> str:
    """Entrypoint handler for the authoriser lambda

    Args:
        event (Dict[str, Any]): Lambda function invocation event
        context (LambdaContext): Lambda function context object

    Returns:
        str: Message and correlation id of the replayed change event
    """
    correlation_id = build_correlation_id()
    logger.set_correlation_id(correlation_id)
    validate_event(event)
    odscode = event["odscode"]
    sequence_number = event["sequence_number"]
    logger.append_keys(ods_code=odscode)
    logger.append_keys(sequence_number=sequence_number)
    change_event = get_change_event(odscode, Decimal(sequence_number))
    org_type_id = change_event.get("OrganisationTypeId")
    logger.append_keys(org_type_id=org_type_id)
    send_change_event(change_event, odscode, int(sequence_number), correlation_id)
    return dumps({"message": "The change event has been re-sent successfully", "correlation_id": correlation_id})


def validate_event(event: Dict[str, Any]) -> None:
    if "odscode" not in event:
        raise ValueError("Missing 'odscode' in event")
    if "sequence_number" not in event:
        raise ValueError("Missing 'sequence_number' in event")


def build_correlation_id():
    return f'{time_ns()}-{getenv("ENV")}-replayed-event'


def get_change_event(odscode: str, sequence_number: Decimal) -> Dict[str, Any]:
    response = client("dynamodb").query(
        TableName=getenv("CHANGE_EVENTS_TABLE_NAME"),
        IndexName="gsi_ods_sequence",
        ProjectionExpression="Event",
        ExpressionAttributeValues={
            ":v1": {
                "S": odscode,
            },
            ":v2": {
                "N": str(sequence_number),
            },
        },
        KeyConditionExpression="ODSCode = :v1 and SequenceNumber = :v2",
        Limit=1,
        ScanIndexForward=False,
    )
    if len(response["Items"]) == 0:
        raise ValueError(f"No change event found for ods code {odscode} and sequence number {sequence_number}")
    item = response["Items"][0]
    logger.info("Retrieved change event from dynamodb", extra={"item": item})
    deserializer = TypeDeserializer()
    change_event = {k: deserializer.deserialize(v) for k, v in item.items()}["Event"]
    logger.append_keys(change_event=change_event)
    logger.info("Found change event")
    return change_event


def send_change_event(change_event: Dict[str, Any], odscode: str, sequence_number: int, correlation_id: str):
    sqs = client("sqs")
    queue_url = sqs.get_queue_url(QueueName=getenv("CHANGE_EVENT_SQS_NAME"))["QueueUrl"]
    logger.info("Sending change event to SQS", extra={"queue_url": queue_url})
    change_event_str = dumps(change_event)
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=change_event_str,
        MessageGroupId=odscode,
        MessageAttributes={
            "correlation-id": {"StringValue": correlation_id, "DataType": "String"},
            "sequence-number": {"StringValue": str(sequence_number), "DataType": "Number"},
        },
    )
    logger.info("Message send to SQS, response from sqs", extra={"response": response})
