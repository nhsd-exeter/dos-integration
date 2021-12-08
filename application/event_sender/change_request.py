from typing import Any, Dict
from change_request_logger import ChangeRequestLogger
from common.utilities import get_environment_variable
from requests import post
from requests.auth import HTTPBasicAuth
from requests.models import Response
class ChangeRequest:
    """Change request class to send change requests"""

    change_request_logger = ChangeRequestLogger()
    headers: Dict[str, str] = {"Content-Type": "application/json", "Accept": "application/json"}
    response: Response

    def __init__(self, change_request_body: Dict[str, Any]) -> None:
        """Initialise the change request class, get environment variables and log change request body

        Args:
            change_request_body (Dict[str, Any]): The change request
        """
        self.change_request_url: str = get_environment_variable("DOS_API_GATEWAY_URL")
        self.timeout: int = int(get_environment_variable("DOS_API_GATEWAY_REQUEST_TIMEOUT"))
        self.authorisation = HTTPBasicAuth(
            get_environment_variable("DOS_API_GATEWAY_USERNAME"),
            get_environment_variable("DOS_API_GATEWAY_PASSWORD"),
        )
        self.change_request_body: Dict[str, Any] = change_request_body
        self.change_request_logger.log_change_request_body(self.change_request_body)

    def post_change_request(self) -> None:
        """Post a change request to the API gateway"""
        try:
            self.response = post(
                url=self.change_request_url,
                headers=self.headers,
                auth=self.authorisation,
                json=self.change_request_body,
                timeout=self.timeout,
            )
            self.change_request_logger.log_change_request_response(self.response)
        except Exception:
            self.change_request_logger.log_change_request_exception()
            raise
