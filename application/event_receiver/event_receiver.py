from json import loads
from logging import getLogger
from os import getenv
from typing import Any, Dict

from aws_lambda_powertools import Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from change_event_exceptions import ValidationException
from change_event_responses import set_return_value
from change_event_validation import validate_event
from common.logger import setup_logger
from common.utilities import invoke_lambda_function, is_mock_mode

tracer = Tracer()
logger = getLogger("lambda")

SUCCESS_STATUS_CODE = 200
FAILURE_STATUS_CODE = 400
UNEXPECTED_SERVER_ERROR_STATUS_CODE = 500
SUCCESS_STATUS_RESPONSE = "Change Event Accepted"
UNEXPECTED_SERVER_ERROR_RESPONSE = "Unexpected server error"


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
        validate_event(change_event)
        trigger_event_processor(change_event)
        logger.info(f"{SUCCESS_STATUS_CODE}|{SUCCESS_STATUS_RESPONSE}")
        return set_return_value(SUCCESS_STATUS_CODE, SUCCESS_STATUS_RESPONSE)
    except ValidationException as exception:  # Expected Error (Deliberately Raised)
        logger.warning(f"{FAILURE_STATUS_CODE}|{str(exception)}")
        return set_return_value(FAILURE_STATUS_CODE, str(exception))
    except Exception as exception:  # Unexpected Error
        logger.critical(f"Expection Occurred: {str(exception)}")
        logger.error(f"{UNEXPECTED_SERVER_ERROR_STATUS_CODE}|{UNEXPECTED_SERVER_ERROR_RESPONSE}")
        return set_return_value(UNEXPECTED_SERVER_ERROR_STATUS_CODE, UNEXPECTED_SERVER_ERROR_RESPONSE)


def extract_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts the change event from the lambda function invocation event,
    also handles if object is passed in not from API Gateway

    Args:
        event (Dict[str, Any]): Lambda function invocation event

    Returns:
        Dict[str, Any]: Lambda function invocation event
    """
    try:
        change_event = loads(event["body"])
    except KeyError:
        logger.exception("Change Event unable to be extracted")
        raise
    return change_event


def trigger_event_processor(change_event: Dict[str, Any]) -> None:
    """Triggers the event processor lambda function

    Args:
        change_event (Dict[str, Any]): Change event to be sent to event processor
    """
    if is_mock_mode() is True:
        logger.info("Mocking mode is set to mock")
    else:
        invoke_lambda_function(getenv("EVENT_PROCESSOR_LAMBDA_NAME"), change_event)
