from logging import getLogger
from typing import Any, Dict

from aws_lambda_powertools import Metrics, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from common.logger import setup_logger

tracer = Tracer()
metrics = Metrics()


@tracer.capture_lambda_handler
@setup_logger
def lambda_handler(event: Dict[str, Any], context: LambdaContext):
    """[summary]

    Args:
        event (Dict[str, Any]): [description]
        context (LambdaContext): [description]
    """
    logger = getLogger("lambda")
    logger.info("Test")
