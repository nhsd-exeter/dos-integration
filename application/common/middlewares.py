from typing import Any

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities.typing import LambdaContext
from botocore.exceptions import ClientError

from common.errors import ValidationError
from common.utilities import extract_body, json_str_body

logger = Logger(child=True)


@lambda_handler_decorator(trace_execution=True)
def redact_staff_key_from_event(handler, event, context: LambdaContext) -> Any:  # noqa: ANN001, ANN401
    """Lambda middleware to remove the 'Staff' key from the Change Event payload.

    Args:
        handler: Lambda handler function
        event: Lambda event
        context: Lambda context object

    Returns:
        Any: Lambda handler response
    """
    logger.info("Checking if 'Staff' key needs removing from Change Event payload")
    if "Records" in event and len(list(event["Records"])) > 0:
        for record in event["Records"]:
            change_event = extract_body(record["body"])
            if change_event.pop("Staff", None) is not None:
                record["body"] = json_str_body(change_event)
                logger.info("Redacted 'Staff' key from Change Event payload")
    return handler(event, context)


@lambda_handler_decorator(trace_execution=True)
def unhandled_exception_logging(handler, event, context: LambdaContext) -> Any:  # noqa: ANN001, ANN401
    """Lambda middleware to log unhandled exceptions.

    Args:
        handler: Lambda handler function
        event: Lambda event
        context: Lambda context object

    Returns:
        Any: Lambda handler response
    """
    try:
        return handler(event, context)
    except ValidationError as error:
        logger.exception(f"Validation Error - {error}", extra={"event": event})  # noqa: TRY401
        return None
    except ClientError as err:
        error_code = err.response["Error"]["Code"]
        error_msg = err.response["Error"]["Message"]
        logger.exception(f"Boto3 Client Error - '{error_code}': {error_msg}", extra={"error": err, "event": event})
        raise
    except BaseException:
        logger.exception("Error Occurred", extra={"event": event})
        raise


@lambda_handler_decorator(trace_execution=True)
def unhandled_exception_logging_hidden_event(handler, event, context: LambdaContext) -> Any:  # noqa: ANN001, ANN401
    """Lambda middleware to log unhandled exceptions but hide the event.

    Args:
        handler: Lambda handler function
        event: Lambda event
        context: Lambda context object

    Returns:
        Any: Lambda handler response
    """
    try:
        return handler(event, context)
    except BaseException:
        logger.exception("Something went wrong but the event is hidden")
        raise
