from http.client import HTTPConnection
from aws_lambda_powertools import Logger
from typing import Any

from common.utilities import is_debug_mode
from requests import Response


class ChangeRequestLogger:
    """Change Request Logging class to log the change request for auditing

    Raises:
        ValueError: Raises ValueError if json response from api-gateway if json isn't valid
    """

    logger = Logger(service="lambda")
    default_log_format = "CHANGE_REQUEST"

    def log_change_request_response(self, response: Response) -> None:
        """Log the change request response for auditing

        Args:
            response (Response): Response object from posting the change request
        """
        if response.ok is True:
            self.logger.info(self.default_log_format)
            self.logger.append_keys(state="Success")
            self.logger.append_keys(response_status_code=response.status_code)
            self.logger.append_keys(response_text=response.text)
        else:
            self.logger.error(self.default_log_format)
            self.logger.append_keys(state="Failure")
            self.logger.append_keys(response_status_code=response.status_code)
            self.logger.append_keys(response_text=response.text)

    def log_change_request_body(self, change_request_body: Any) -> None:
        """Log the change request body for auditing

        Args:
            change_request_body (Any): Change request body to be logged
        """
        self.logger.info(self.default_log_format)
        self.logger.append_keys(change_request_body=change_request_body)

        if is_debug_mode():
            HTTPConnection.debuglevel = 1

    def log_change_request_exception(self) -> None:
        self.logger.exception(self.default_log_format)
        self.logger.append_keys(state="Exception")
        self.logger.append_keys(exception_reason="Error posting change request")
