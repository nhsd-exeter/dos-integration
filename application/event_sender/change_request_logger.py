from http.client import HTTPConnection
from logging import getLogger
from typing import Any

from common.utilities import is_debug_mode
from requests import Response


class ChangeRequestLogger:
    """Change Request Logging class to log the change request for auditing

    Raises:
        ValueError: Raises ValueError if json response from api-gateway if json isn't valid
    """

    logger = getLogger("lambda")
    default_log_format = "CHANGE_REQUEST"

    def log_change_request_response(self, response: Response) -> None:
        """Log the change request response for auditing

        Args:
            response (Response): Response object from posting the change request
        """
        if response.ok is True:
            self.logger.info(f"{self.default_log_format}|Success|{response.status_code}|{response.text}")
        elif response.ok is False:
            self.logger.error(f"{self.default_log_format}|Failure|{response.status_code}|{response.text}")

    def log_change_request_body(self, change_request_body: Any) -> None:
        """Log the change request body for auditing

        Args:
            change_request_body (Any): Change request body to be logged
        """
        self.logger.info(f"{self.default_log_format}|{change_request_body=}")
        if is_debug_mode():
            HTTPConnection.debuglevel = 1

    def log_change_request_exception(self) -> None:
        self.logger.exception(f"{self.default_log_format}|Exception|Error posting change request")
