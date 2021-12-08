from typing import Any, Dict

from aws_lambda_powertools import Tracer
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from change_request import ChangeRequest

# from common.logger import setup_logger

tracer = Tracer()
logger = Logger()


@tracer.capture_lambda_handler()
@logger.inject_lambda_context()
# @setup_logger
def lambda_handler(event: Dict[str, Any], context: LambdaContext):
    """Entrypoint handler for the event_sender lambda

    Args:
        event (Dict[str, Any]): Lambda function invocation event
        context (LambdaContext): Lambda function context object
    """
    logger.debug("Checking out the context", extra={"context": context.client_context})
    logger.set_correlation_id(context.client_context.custom.correlation_id)
    change_request = ChangeRequest(event)
    change_request.post_change_request()
