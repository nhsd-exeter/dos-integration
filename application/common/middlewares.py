from aws_lambda_powertools import Logger
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities.data_classes import SQSEvent
from aws_lambda_powertools.utilities.typing import LambdaContext

from event_processor.change_event_exceptions import ValidationException


logger = Logger(child=True)


@lambda_handler_decorator(trace_execution=True)
def unhandled_exception_logging(handler, event, context: LambdaContext):
    try:
        response = handler(event, context)
        return response
    except ValidationException as err:
        logger.exception("Validation Error", extra={"error": err, "event": event})
        return
    except BaseException as err:
        logger.exception("Something went wrong", extra={"error": err, "event": event})
        raise


@lambda_handler_decorator(trace_execution=True)
def set_correlation_id(handler, event: SQSEvent, context: LambdaContext):
    """Set correlation id from SQS event"""
    record = next(event.records)
    logger.set_correlation_id(record.message_attributes["correlation-id"]["stringValue"])
    response = handler(event, context)
    return response
