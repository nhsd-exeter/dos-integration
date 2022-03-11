from os import getenv
from typing import Any, Dict
from aws_lambda_powertools import Logger
from change_request_logger import ChangeRequestLogger
from requests import post
from requests.auth import HTTPBasicAuth
from requests.models import Response
from common.aws import get_secret

logger = Logger(child=True)


class ChangeRequest:
    """Change request class to send change requests"""

    change_request_logger = ChangeRequestLogger()
    headers: Dict[str, str] = {"Content-Type": "application/json", "Accept": "application/json"}

    def __init__(self, change_request_body: Dict[str, Any]) -> None:
        """Initialise the change request class, get environment variables and log change request body

        Args:
            change_request_body (Dict[str, Any]): The change request
        """
        self.change_request_url: str = getenv("DOS_API_GATEWAY_URL")
        self.timeout: int = int(getenv("DOS_API_GATEWAY_REQUEST_TIMEOUT"))
        secrets = get_secret(getenv("DOS_API_GATEWAY_SECRETS"))
        self.authorisation = HTTPBasicAuth(
            secrets[getenv("DOS_API_GATEWAY_USERNAME_KEY")],
            secrets[getenv("DOS_API_GATEWAY_PASSWORD_KEY")],
        )
        self.change_request_body: Dict[str, Any] = change_request_body

    def post_change_request(self, is_health_check: bool) -> Response:
        self.change_request_logger.log_change_request_post_attempt(self.change_request_body)
        """Post a change request to the API gateway"""
        try:
            response = post(
                url=self.change_request_url,
                headers=self.headers,
                auth=self.authorisation,
                json=self.change_request_body,
                timeout=self.timeout,
            )
            if not is_health_check:
                self.change_request_logger.log_change_request_response(response)
            return response
        except Exception:
            self.change_request_logger.log_change_request_exception()
