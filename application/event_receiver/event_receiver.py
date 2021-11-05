from logging import getLogger
from os import getenv
from typing import Any, Dict

import boto3
from aws_lambda_powertools import Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from common.logger import setup_logger
from common.utilities import is_mock_mode
from event_validation import validate_event

tracer = Tracer()
logger = getLogger("lambda")


@tracer.capture_lambda_handler()
@setup_logger
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """Entrypoint handler for the event_receiver lambda

    Args:
        event (Dict[str, Any]): Lambda function invocation event
        context (LambdaContext): Lambda function context object
    """
    if validate_event(event) is False:
        message = "Bad Change Event Received"
        status_code = 400
    else:
        trigger_event_processor()
        message = "Change Event Accepted"
        status_code = 200
    return get_return_value(status_code, message)


def get_return_value(status_code: int, message: str) -> Dict[str, Any]:
    """Returns the return value for the lambda function

    Args:
        status_code (int): [description]
        message (str): [description]

    Returns:
        Dict[str, Any]: [description]
    """
    return {"statusCode": status_code, "body": message}


def trigger_event_processor() -> None:
    """Triggers the event processor lambda function"""
    if is_mock_mode():
        logger.info("Mocking mode is set to mock")
    else:
        client = boto3.client("lambda")
        client.invoke(FunctionName=getenv("EVENT_PROCESSOR_NAME"), InvocationType="Event")
