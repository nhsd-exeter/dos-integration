from logging import Filter, Logger, LogRecord, getLogger
from logging.config import fileConfig
from os import environ, getenv, path
from typing import Any, Dict

from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities.typing import LambdaContext


@lambda_handler_decorator
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
    logger.addFilter(LambdaFilter(context))
    return handler(event, context)


def import_logger_from_file() -> None:
    """Import logging config from logging.conf"""
    logging_path = path.join(path.dirname(__file__), "logging.conf")
    fileConfig(logging_path, disable_existing_loggers=True)


def set_log_level(logger: Logger) -> Logger:
    """Sets the log level from environment variable LOG_LEVEL

    Args:
        logger (Logger): Lambda function logger

    Returns:
        Logger: returns logger set to correct logging level
    """
    log_level = environ["LOG_LEVEL"]
    logger.setLevel(log_level)
    logger.debug(f"Logger set to {log_level} mode")
    return logger


class LambdaFilter(Filter):
    """The filter to be added to the lambda logger to add custom fields to logs

    Args:
        Filter (Class): The logging filter class to extend
    """

    def __init__(self, context: LambdaContext) -> None:
        """Set context variables to filter LambdaFilter class variables

        Args:
            context (LambdaContext): Lambda function context object
        """
        self.function_name = context.function_name
        self.aws_request_id = context.aws_request_id
        x_ray_trace_id = getenv("_X_AMZN_TRACE_ID")
        if x_ray_trace_id is None:
            x_ray_trace_id = "00000-00000-00000"
        self.x_ray_trace_id = x_ray_trace_id

    def filter(self, record: LogRecord) -> bool:
        """Sets custom variables to the logging format

        Args:
            record (LogRecord): A log record

        Returns:
            bool: return True if the record is to be processed
        """
        record.function_name = self.function_name
        record.aws_request_id = self.aws_request_id
        record.x_ray_trace_id = self.x_ray_trace_id
        return True
