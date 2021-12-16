from aws_lambda_powertools import Logger
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities.data_classes import SQSEvent
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger(child=True)


@lambda_handler_decorator(trace_execution=True)
def unhandled_exception_logging(handler, event, context: LambdaContext):
    try:
        response = handler(event, context)
        return response
    except BaseException as err:
        logger.exception("Something went wrong", extra={"error": err})
        raise


@lambda_handler_decorator(trace_execution=True)
def set_correlation_id(handler, event: SQSEvent, context: LambdaContext):
    """Set correlation id from SQS event"""
    logger.set_correlation_id(next(event.records).message_attributes["correlation-id"]["stringValue"])
    response = handler(event, context)
    return response
