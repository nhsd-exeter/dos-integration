from logging import Filter, LogRecord
from os import getenv

from aws_lambda_powertools.utilities.typing import LambdaContext


class LogFilter(Filter):
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
        self.x_ray_trace_id = "NA"
        if getenv("_X_AMZN_TRACE_ID") is not None:
            self.x_ray_trace_id = getenv("_X_AMZN_TRACE_ID").split(";")[0].split("=")[1]

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
