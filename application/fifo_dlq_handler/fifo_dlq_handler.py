import hashlib
from decimal import Decimal
from json import dumps, loads
from os import environ
from time import time
from typing import Any, Dict

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from common.dynamodb import add_change_request_to_dynamodb
from common.middlewares import set_correlation_id, unhandled_exception_logging
from common.utilities import extract_body, get_sequence_number

TTL = 157680000  # int((365*5)*24*60*60) . 5 years in seconds
tracer = Tracer()
logger = Logger()
FIFO_DLQ_HANDLER_REPORT_ID = "FIFO_DLQ_HANDLER_RECEIVED_EVENT"


@unhandled_exception_logging()
@tracer.capture_lambda_handler()
@event_source(data_class=SQSEvent)
@set_correlation_id()
@logger.inject_lambda_context()
def lambda_handler(event: SQSEvent, context: LambdaContext) -> None:
    """Entrypoint handler for the lambda

    Args:
        event (SQSEvent): Lambda function invocation event (list of 1 SQS Message)
        context (LambdaContext): Lambda function context object
    """
    record = next(event.records)
    message = record.body
    logger.warning(
        "Dead Letter Queue Handler received event",
        extra={
            "report_key": FIFO_DLQ_HANDLER_REPORT_ID,
            "dlq_event": message,
        },
    )
    change_event = extract_body(message)
    sqs_timestamp = str(record.attributes["SentTimestamp"])
    sequence_number = get_sequence_number(record)
    add_change_request_to_dynamodb(change_event, sequence_number, sqs_timestamp)
