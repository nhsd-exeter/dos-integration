from json import dumps
from logging import Logger, getLogger
from os import environ
from typing import Any, Dict

from change_request_logger import ChangeRequestLogger
from requests import post
from requests.auth import HTTPBasicAuth


class ChangeRequest:
    logger: Logger = getLogger("lambda")
    change_request_logger = ChangeRequestLogger()
    headers: Dict[str, str] = {"Content-Type": "application/json", "Accept": "application/json"}
    response: None = None

    def __init__(self, change_request_json: Dict[str, Any]) -> None:
        self.change_request_url: str = self.get_environment_variable("CHANGE_REQUEST_ENDPOINT_URL")
        self.timeout: int = int(self.get_environment_variable("CHANGE_REQUEST_ENDPOINT_TIMEOUT"))
        self.api_gateway_username: str = self.get_environment_variable("API_GATEWAY_USERNAME")
        self.api_gateway_password: str = self.get_environment_variable("API_GATEWAY_PASSWORD")
        self.change_request_json: Dict[str, Any] = change_request_json
        self.change_request_logger.log_change_request_body(self.change_request_json)

    def post_change_request(self) -> None:
        authorisation = HTTPBasicAuth(self.api_gateway_username, self.api_gateway_password)
        response = post(
            url=self.change_request_url,
            headers=self.headers,
            auth=authorisation,
            json=self.change_request_json,
            timeout=self.timeout,
        )
        self.response = response
        self.change_request_logger.log_change_request_response(response)

    def get_environment_variable(self, environment_key: str) -> str:
        try:
            return environ[environment_key]
        except KeyError as e:
            self.logger.exception(f"Environment variable not found {environment_key}")
            raise e
