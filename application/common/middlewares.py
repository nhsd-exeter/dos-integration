from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities.typing import LambdaContext
from botocore.exceptions import ClientError

from common.errors import ValidationException

logger = Logger(child=True)


@lambda_handler_decorator(trace_execution=True)
def unhandled_exception_logging(handler, event, context: LambdaContext):
    try:
        response = handler(event, context)
        return response
    except ValidationException as err:
        logger.exception(f"Validation Error - {err}", extra={"error": err, "event": event})
        return
    except ClientError as err:
        error_code = err.response["Error"]["Code"]
        error_msg = err.response["Error"]["Message"]
        logger.exception(f"Boto3 Client Error - '{error_code}': {error_msg}", extra={"error": err, "event": event})
        raise err
    except BaseException as err:
        logger.exception(f"Something went wrong - {err}", extra={"error": err, "event": event})
        raise err


@lambda_handler_decorator(trace_execution=True)
def unhandled_exception_logging_hidden_event(handler, event, context: LambdaContext):
    try:
        response = handler(event, context)
        return response
    except BaseException as err:
        logger.error("Something went wrong but the event is hidden")
        raise err
