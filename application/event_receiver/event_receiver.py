from json import dumps, loads
from logging import getLogger
from os import getenv
from typing import Any, Dict

from aws_lambda_powertools import Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from change_event_exceptions import ValidationException
from change_event_responses import set_return_value
from change_event_validation import valid_event
from common.logger import setup_logger
from common.utilities import invoke_lambda_function, is_mock_mode

tracer = Tracer()
logger = getLogger("lambda")

SUCCESS_STATUS_CODE = 200
FAILURE_STATUS_CODE = 400
SUCCESS_STATUS_RESPONSE = "Change Event Accepted"
GENERIC_FAILURE_STATUS_RESPONSE = "Event malformed, validation failed"


@tracer.capture_lambda_handler()
@setup_logger
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """Entrypoint handler for the event_receiver lambda

    Args:
        event (Dict[str, Any]): Lambda function invocation event
        context (LambdaContext): Lambda function context object
    """
    try:
        change_event = extract_event(event)
        if valid_event(change_event) is True:
            trigger_event_processor()
        else:
            raise ValidationException(GENERIC_FAILURE_STATUS_RESPONSE)

        logger.info(f"{SUCCESS_STATUS_CODE}|{SUCCESS_STATUS_RESPONSE}")
        return set_return_value(SUCCESS_STATUS_CODE, SUCCESS_STATUS_RESPONSE)

    except Exception as exception:
        logger.error(f"{FAILURE_STATUS_CODE}|{str(exception)}")
        return set_return_value(FAILURE_STATUS_CODE, str(exception))


def extract_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts the change event from the lambda function invocation event,
    also handles if object is passed in not from API Gateway

    Args:
        event (Dict[str, Any]): Lambda function invocation event

    Returns:
        Dict[str, Any]: Lambda function invocation event
    """
    try:
        string_event = dumps(event["body"])
        change_event = loads(string_event)
    except KeyError:
        logger.exception("Change Event failed transformations")
        raise ValidationException("Change Event incorrect format")
    return change_event


def trigger_event_processor() -> None:
    """Triggers the event processor lambda function"""
    if is_mock_mode() is True:
        logger.info("Mocking mode is set to mock")
    else:
        invoke_lambda_function(getenv("EVENT_PROCESSOR_NAME"))
