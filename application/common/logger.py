from logging import INFO, Logger, getLogger
from logging.config import fileConfig
from os import getenv, path
from typing import Any, Dict

from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities.typing import LambdaContext

from .log_filter import LogFilter


@lambda_handler_decorator(trace_execution=True)
def setup_logger(handler: Any, event: Dict[str, Any], context: LambdaContext) -> Any:
    """Middleware function that sets up the logger for use in the rest of the lambda

    Args:
        handler (function): Lambda function handler
        event (Dict[str, Any]): Lambda function invocation event
        context (LambdaContext): Lambda function context object
    Returns:
        function: The lambda invocation object which includes the event and context
    """
    import_logger_from_file()
    logger = getLogger("lambda")
    logger = set_log_level(logger)
    logger.addFilter(LogFilter(context))
    return handler(event, context)


def import_logger_from_file() -> None:
    """Import logging config from logging.conf"""
    try:
        logging_path = path.join(path.dirname(__file__), "logging.conf")
        fileConfig(logging_path, disable_existing_loggers=True)
    except KeyError as e:
        print("Can't find logging config file")
        raise e


def set_log_level(logger: Logger) -> Logger:
    """Sets the log level from environment variable LOG_LEVEL

    Args:
        logger (Logger): Lambda function logger

    Returns:
        Logger: returns logger set to correct logging level
    """
    log_level = getenv("LOG_LEVEL")
    if log_level is None:
        print("LOG_LEVEL environment variable not set")
        log_level = INFO
        print(f"LOG_LEVEL has been set to default {log_level}")
    logger.setLevel(log_level)
    return logger
