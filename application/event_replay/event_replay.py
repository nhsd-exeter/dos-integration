from decimal import Decimal
from os import getenv
from time import time_ns
from typing import Any, Dict

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from boto3 import client
from boto3.dynamodb.types import TypeDeserializer
from common.middlewares import unhandled_exception_logging
from simplejson import dumps

tracer = Tracer()
logger = Logger()


@tracer.capture_lambda_handler()
@unhandled_exception_logging
@logger.inject_lambda_context
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """Entrypoint handler for the authoriser lambda

    Args:
        event (Dict[str, Any]): Lambda function invocation event
        context (LambdaContext): Lambda function context object

    Returns:
        dict: Policy to allow connection to the API Gateway Mock
    """
    body = event
    odscode = body["odscode"]
    logger.append_keys(ods_code=odscode)
    sequence_number = body["sequence_number"]
    logger.append_keys(sequence_number=sequence_number)
    # logger.append_keys(dynamo_record_id=dynamo_record_id)
    change_event = get_change_event(odscode, Decimal(sequence_number))
    correlation_id = build_correlation_id()
    logger.set_correlation_id(correlation_id)
    # change_event = fix_decimals(change_event)
    send_change_event(change_event, odscode, int(sequence_number), correlation_id)
    return dumps({"message": "OK"})


def build_correlation_id():
    return f'{time_ns()}-{getenv("PROFILE")}'


def get_change_event(odscode: str, sequence_number: Decimal):
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
    item = response["Items"][0]
    logger.info("Retrieved change event", extra={"item": item})
    deserializer = TypeDeserializer()
    change_event = {k: deserializer.deserialize(v) for k, v in item.items()}["Event"]
    logger.append_keys(change_event=change_event)
    return change_event


# def fix_decimals(change_event: Dict[str, Any]):
#     for k, v in change_event.items():
#         if isinstance(v, Decimal):
#             change_event[k] = float(v)
#     return change_event


def send_change_event(change_event: Dict[str, Any], odscode: str, sequence_number: int, correlation_id: str):
    sqs = client("sqs")
    queue_url = sqs.get_queue_url(QueueName=getenv("FIFO_SQS_NAME"))["QueueUrl"]
    logger.info("Sending change event to SQS", extra={"queue_url": queue_url, "sequence_number": sequence_number})
    change_event_str = dumps(change_event)
    # print(message_body)
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=change_event_str,
        MessageGroupId=odscode,
        MessageAttributes={
            "correlation-id": {"StringValue": correlation_id, "DataType": "String"},
            "sequence-number": {"StringValue": str(sequence_number), "DataType": "Number"},
        },
    )


# {"odscode":"FQ582", "sequence_number": "1644322266020278800"}
