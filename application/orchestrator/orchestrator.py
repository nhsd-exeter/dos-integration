from json import dumps
from os import getenv
from time import sleep
from typing import Any, Dict

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from boto3 import client
from common.middlewares import unhandled_exception_logging
from common.utilities import extract_body
from common.types import ChangeMetadata, ChangeRequestQueueItem

logger = Logger()
tracer = Tracer()
TIME_TO_SLEEP = 1 / int(getenv("SLEEP_TIME_IN_SECONDS", default=1))
QUEUE_URL = getenv("CR_QUEUE_URL")


@unhandled_exception_logging()
@tracer.capture_lambda_handler()
@logger.inject_lambda_context
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> None:
    """Entrypoint handler for the orchestrator lambda

    Args:
        event (Dict[str, Any]): Lambda function invocation event
        context (LambdaContext): Lambda function context object

    Event: The event payload should contain a Change Request
    """
    sqs = client("sqs")
    response = sqs.receive_message(QueueUrl=QUEUE_URL, MaxNumberOfMessages=10, MessageAttributeNames=["All"])
    logger.info(f"Received {len(response['Messages'])} messages from SQS")
    lambda_client = client("lambda")
    # TODO: Need to figure out circuit breaker bits
    for message in response["Messages"]:
        logger.info("Processing SQS message", extra={"message": message})
        change_metadata: ChangeMetadata = {
            "dynamo_record_id": message["MessageAttributes"]["DynamoRecordId"]["StringValue"],
            "correlation_id": message["MessageAttributes"]["CorrelationId"]["StringValue"],
            "message_received": int(message["MessageAttributes"]["MessageReceived"]["StringValue"]),
            "ods_code": message["MessageAttributes"]["OdsCode"]["StringValue"],
        }
        change_request_queue_item: ChangeRequestQueueItem = {
            "change_request": extract_body(message["Body"]),
            "recipient_id": message["ReceiptHandle"],
            "metadata": change_metadata,
        }
        invoke_lambda(lambda_client, change_request_queue_item)
        sleep(TIME_TO_SLEEP)


def invoke_lambda(lambda_client, payload: Dict[str, Any]) -> Dict[str, Any]:
    response = lambda_client.invoke(
        FunctionName=getenv("EVENT_SENDER_FUNCTION_NAME"),
        InvocationType="event",
        Payload=dumps(payload),
    )
    return response
