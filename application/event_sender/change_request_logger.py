from http.client import HTTPConnection
from logging import getLogger
from os import getenv

from requests import Response


class ChangeRequestLogger:
    logger = getLogger("lambda")

    def log_change_request_response(self, response: Response) -> None:
        if response.ok is True:
            self.logger.info(f"CHANGE_REQUEST|Success|{response.status_code}|{response.json()}")
        elif response.ok is False:
            self.logger.error(f"CHANGE_REQUEST|Failure|{response.status_code}|{response.json()}")

    def log_change_request_body(self, change_request_json: str) -> None:
        self.logger.info(f"CHANGE_REQUEST|{change_request_json=}")
        if getenv("PROFILE") in ["task", "local"]:
            HTTPConnection.debuglevel = 1
