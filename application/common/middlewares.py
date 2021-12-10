from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger

logger = Logger(child=True)


@lambda_handler_decorator(trace_execution=True)
def unhandled_exception_logging(handler, event, context):
    try:
        response = handler(event, context)
        return response
    except BaseException as err:
        logger.exception("Something went wrong", extra={"error": err})
        raise


@lambda_handler_decorator(trace_execution=True)
def set_correlation_id_if_none_set(handler, event, context: LambdaContext):

    correlation_id = logger.get_correlation_id()

    if correlation_id is None:
        logger.set_correlation_id(context.aws_request_id)

    response = handler(event, context)
    return response
