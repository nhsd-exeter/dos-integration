from aws_lambda_powertools import Logger
from typing import Any

from requests import Response

logger = Logger(child=True)


class ChangeRequestLogger:
    """Change Request Logging class to log the change request for auditing

    Raises:
        ValueError: Raises ValueError if json response from api-gateway if json isn't valid
    """

    def log_change_request_post_attempt(self, change_request_body: Any) -> None:
        """Log before attempting to POST change request to DoS API Gateway"""

        logger.info("Attempting to send change request to DoS", extra={"change_request_body": change_request_body})

    def log_change_request_response(self, response: Response) -> None:
        """Log the change request response for auditing

        Args:
            response (Response): Response object from posting the change request
        """
        if response.ok is True:
            extra = {"state": "Success", "response_status_code": response.status_code, "response_text": response.text}
            logger.info("Successfully send change request to DoS", extra=extra)
        else:
            extra = {"state": "Failure", "response_status_code": response.status_code, "response_text": response.text}
            logger.error("Failed to send change request to DoS", extra=extra)

    def log_change_request_exception(self) -> None:
        extra = {"state": "Exception", "exception_reason": "Error posting change request"}
        logger.exception("Exception error posting change request to DoS", extra=extra)
