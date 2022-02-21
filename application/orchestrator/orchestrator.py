from json import dumps
from os import getenv, environ
from time import sleep
from typing import Any, Dict

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from boto3 import client
from common.dynamodb import get_circuit_status
from common.middlewares import unhandled_exception_logging
from common.utilities import extract_body
from common.types import ChangeMetadata, ChangeRequestQueueItem
from time import strftime, gmtime, time

logger = Logger()
tracer = Tracer()
TIME_TO_SLEEP = 1 / int(getenv("DOS_TRANSACTIONS_PER_SECOND", default=3))
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
    lambda_client = client("lambda")
    start = time()
    loop = 0

    while time() < start + 280:
        circuit_open = get_circuit_status(environ["CIRCUIT"])
        if circuit_open:
            # Wait then continue
            sleep(environ["SLEEP_FOR_WHEN_OPEN"])
            change_request_queue_item: ChangeRequestQueueItem = {
                "is_health_check": True,
                "change_request": {},
                "recipient_id": None,
                "metadata": None,
            }
            logger.info(
                "Sending health check to try and re-open the circuit", extra={"request": change_request_queue_item}
            )
            invoke_lambda(lambda_client, change_request_queue_item)

            continue

        logger.append_keys(loop=loop)
        response = sqs.receive_message(QueueUrl=QUEUE_URL, MaxNumberOfMessages=10, MessageAttributeNames=["All"])
        messages = response.get("Messages")
        if messages is None:
            logger.info("No messages at this time")
            sleep(1)
        else:
            logger.info(f"Received {len(messages)} messages from SQS")

            # TODO: Need to figure out circuit breaker bits
            for message in messages:
                it_start = time()
                logger.info("Processing SQS message", extra={"sqs_message": message})
                correlation_id = message["MessageAttributes"]["correlation_id"]["StringValue"]
                dynamo_record_id = message["MessageAttributes"]["dynamo_record_id"]["StringValue"]
                message_received = int(message["MessageAttributes"]["message_received"]["StringValue"])
                ods_code = message["MessageAttributes"]["ods_code"]["StringValue"]
                logger.set_correlation_id(correlation_id)
                logger.append_keys(ods_code=ods_code)
                s, ms = divmod(message_received, 1000)
                message_received_pretty = "%s.%03d" % (strftime("%Y-%m-%d %H:%M:%S", gmtime(s)), ms)
                logger.append_keys(message_received=message_received_pretty)
                logger.append_keys(dynamo_record_id=dynamo_record_id)
                logger.append_keys(ods_code=ods_code)
                change_metadata: ChangeMetadata = {
                    "dynamo_record_id": dynamo_record_id,
                    "correlation_id": correlation_id,
                    "message_received": message_received,
                    "ods_code": ods_code,
                }
                change_request_queue_item: ChangeRequestQueueItem = {
                    "is_health_check": False,
                    "change_request": extract_body(message["Body"]),
                    "recipient_id": message["ReceiptHandle"],
                    "metadata": change_metadata,
                }
                # TODO: What happens when this fails?
                logger.info("Sending request to event sender", extra={"request": change_request_queue_item})
                invoke_lambda(lambda_client, change_request_queue_item)
                it_end = time()
                to_sleep = max(0, (TIME_TO_SLEEP - (it_end - it_start)))
                logger.debug(f"Seeping for {to_sleep}")
                sleep(to_sleep)
        loop = loop + 1


def invoke_lambda(lambda_client, payload: Dict[str, Any]) -> Dict[str, Any]:
    response = lambda_client.invoke(
        FunctionName=getenv("EVENT_SENDER_FUNCTION_NAME"),
        InvocationType="Event",
        Payload=dumps(payload),
    )
    return response
