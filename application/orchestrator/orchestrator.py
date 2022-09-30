from json import dumps
from os import environ, getenv
from time import gmtime, sleep, strftime, time
from typing import Any, Dict

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.tracing import Tracer
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from boto3 import client

from common.dynamodb import get_circuit_is_open
from common.middlewares import unhandled_exception_logging
from common.types import UpdateRequestMetadata, UpdateRequestQueueItem
from common.utilities import extract_body

logger = Logger()
tracer = Tracer()
QUEUE_URL = getenv("UPDATE_REQUEST_QUEUE_URL")
sqs_client = client("sqs")
lambda_client = client("lambda")


@unhandled_exception_logging()
@tracer.capture_lambda_handler()
@logger.inject_lambda_context
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> None:
    """Entrypoint handler for the orchestrator lambda

    Args:
        event (Dict[str, Any]): Lambda function invocation event
        context (LambdaContext): Lambda function context object

    Event: The event payload should contain an Update Request
    """
    start = time()
    loop = 0
    TIME_TO_SLEEP = 1 / int(getenv("DOS_TRANSACTIONS_PER_SECOND", default=3))
    while time() < start + int(environ["RUN_FOR"]):
        if get_circuit_is_open(environ["CIRCUIT"]):
            # Wait then continue
            sleep(int(environ["SLEEP_FOR_WHEN_OPEN"]))
            update_request_queue_item = UpdateRequestQueueItem(
                is_health_check=True, update_request=None, recipient_id=None, metadata=None
            )
            logger.info(
                "Sending health check to try and re-open the circuit", extra={"request": update_request_queue_item}
            )
            invoke_lambda(update_request_queue_item)
            continue

        logger.append_keys(loop=loop)
        response = sqs_client.receive_message(QueueUrl=QUEUE_URL, MaxNumberOfMessages=10, MessageAttributeNames=["All"])
        messages = response.get("Messages")
        if messages is None:
            logger.info("No messages at this time")
            sleep(1)
        else:
            logger.info(f"Received {len(messages)} messages from SQS")

            for message in messages:
                it_start = time()
                logger.info("Processing SQS message", extra={"sqs_message": message})
                correlation_id: str = message["MessageAttributes"]["correlation_id"]["StringValue"]
                dynamo_record_id: str = message["MessageAttributes"]["dynamo_record_id"]["StringValue"]
                message_received: int = int(message["MessageAttributes"]["message_received"]["StringValue"])
                ods_code: str = message["MessageAttributes"]["ods_code"]["StringValue"]
                logger.set_correlation_id(correlation_id)
                s, ms = divmod(message_received, 1000)
                message_received_pretty = "%s.%03d" % (strftime("%Y-%m-%d %H:%M:%S", gmtime(s)), ms)
                update_request_metadata = UpdateRequestMetadata(
                    dynamo_record_id=dynamo_record_id,
                    correlation_id=correlation_id,
                    message_received=message_received,
                    ods_code=ods_code,
                    message_deduplication_id=message["MessageAttributes"]["message_deduplication_id"]["StringValue"],
                    message_group_id=message["MessageAttributes"]["message_group_id"]["StringValue"],
                )
                update_request_queue_item = UpdateRequestQueueItem(
                    is_health_check=False,
                    update_request=extract_body(message["Body"]),
                    recipient_id=message["ReceiptHandle"],
                    metadata=update_request_metadata,
                )
                logger.info(
                    "Sending request to service sync",
                    extra={
                        "request": update_request_queue_item,
                        "message_received": message_received_pretty,
                        "dynamo_record_id": dynamo_record_id,
                        "ods_code": ods_code,
                    },
                )
                invoke_lambda(update_request_queue_item)
                it_end = time()
                to_sleep = max(0, (TIME_TO_SLEEP - (it_end - it_start)))
                # If ever 0 is slept we are over the limit,
                # We are unable to improve performance without changing the logic or cpu count
                logger.debug(f"Sleeping for {to_sleep}")
                sleep(to_sleep)
        loop = loop + 1


def invoke_lambda(payload: Dict[str, Any]) -> Dict[str, Any]:
    return lambda_client.invoke(
        FunctionName=getenv("EVENT_SENDER_FUNCTION_NAME"),
        InvocationType="Event",
        Payload=dumps(payload),
    )  # type: ignore
