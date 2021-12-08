from typing import Any, Dict

from aws_lambda_powertools import Tracer
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from change_request import ChangeRequest

# from common.logger import setup_logger

tracer = Tracer()
logger = Logger()


@tracer.capture_lambda_handler()
@logger.inject_lambda_context(correlation_id_path="context.custom.correlation_id")
# @setup_logger
def lambda_handler(event: Dict[str, Any], context: LambdaContext):
    """Entrypoint handler for the event_sender lambda

    Args:
        event (Dict[str, Any]): Lambda function invocation event
        context (LambdaContext): Lambda function context object
    """
    change_request = ChangeRequest(event)
    change_request.post_change_request()
