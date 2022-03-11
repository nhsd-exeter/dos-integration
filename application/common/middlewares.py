from aws_lambda_powertools import Logger
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities.data_classes import SQSEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from botocore.exceptions import ClientError

from common.change_event_exceptions import ValidationException


logger = Logger(child=True)


@lambda_handler_decorator(trace_execution=True)
def unhandled_exception_logging(handler, event, context: LambdaContext):
    try:
        response = handler(event, context)
        return response
    except ValidationException as err:
        logger.exception("Validation Error", extra={"error": err, "event": event})
        return
    except ClientError as err:
        error_code = err.response["Error"]["Code"]
        error_msg = err.response["Error"]["Message"]
        logger.exception(f"Boto3 Client Error - '{error_code}': {error_msg}", extra={"error": err, "event": event})
        raise err
    except BaseException as err:
        logger.exception(f"Something went wrong - {str(err)}", extra={"error": err, "event": event})
        raise err


@lambda_handler_decorator(trace_execution=True)
def set_correlation_id(handler, event: SQSEvent, context: LambdaContext):
    """Set correlation id from SQS event"""
    record = next(event.records)
    logger.set_correlation_id(record.message_attributes["correlation-id"]["stringValue"])
    response = handler(event, context)
    return response
