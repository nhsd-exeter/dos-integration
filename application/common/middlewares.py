from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.data_classes import event_source, SQSEvent
from botocore.exceptions import ClientError

from common.errors import ValidationException
from common.utilities import extract_body, json_str_body

logger = Logger(child=True)

@lambda_handler_decorator(trace_execution=True)
def redact_staff_key_from_event(handler, event: SQSEvent, context: LambdaContext):
    logger.info(f"Checking if 'Staff' key needs removing from Change Event payload {event}", extra={"event": event})
    if len(list(event.records)) > 0:
            for record in event.records:
                change_event = extract_body(record.body)
                if change_event.pop('Staff', None) != None:
                    record = json_str_body(change_event)
                    logger.info("Redacted 'Staff' key from Change Event payload")
    return handler(event, context)


@lambda_handler_decorator(trace_execution=True)
def unhandled_exception_logging(handler, event, context: LambdaContext):
    if isinstance(event, SQSEvent):
        # raw_event = event.raw_event
        raw_event = str(event)
    else:
        raw_event = event

    try:
        response = handler(event, context)
        return response
    except ValidationException as err:
        logger.exception(f"Validation Error - {err}", extra={"error": err, "event": raw_event})
        return
    except ClientError as err:
        error_code = err.response["Error"]["Code"]
        error_msg = err.response["Error"]["Message"]
        logger.exception(f"Boto3 Client Error - '{error_code}': {error_msg}", extra={"error": err, "event": raw_event})
        raise err
    except BaseException as err:
        logger.exception(f"Something went wrong - {err}", extra={"error": err, "event": raw_event})
        raise err


@lambda_handler_decorator(trace_execution=True)
def unhandled_exception_logging_hidden_event(handler, event, context: LambdaContext):
    try:
        response = handler(event, context)
        return response
    except BaseException as err:
        logger.error("Something went wrong but the event is hidden")
        raise err
