from os import getenv
from typing import Any

from requests import put
from requests.models import Response

# Mock Server Website: https://www.mock-server.com/
# API documentation: https://app.swaggerhub.com/apis/jamesdbloom/mock-server-openapi/5.11.x#/expectation/put_expectation
# Local Dashboard: http://localhost:1080/mockserver/dashboard


class MockServer:
    mockserver_server = None
    headers = {"Content-Type": "application/json"}
    response: Response
    status_code: int

    def __init__(self) -> None:
        self.mockserver_server = getenv("MOCKSERVER_URL")

    def reset_server(self) -> None:
        self.put("/reset", {})

    def put(self, path: str, body: Any) -> None:
        self.response = put(url=self.mockserver_server + path, headers=self.headers, json=body)
        self.status_code = self.response.status_code

    def assert_status_code(self, status_code: int) -> None:
        assert self.status_code == status_code
