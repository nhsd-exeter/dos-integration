from os import getenv
from typing import Any

from requests import put
from requests.models import Response

# Mock Server Website - https://www.mock-server.com/
# For API documentation see here - https://app.swaggerhub.com/apis/jamesdbloom/mock-server-openapi/5.11.x#/expectation/put_expectation
# Local Dashboard - http://localhost:1080/mockserver/dashboard


class MockServer:
    mockserver_server = None
    headers = {"Content-Type": "application/json"}

    def __init__(self) -> None:
        self.mockserver_server = getenv("MOCKSERVER_URL")

    def reset_server(self) -> None:
        self.put("/reset", {})

    def put(self, path: str, body: Any) -> Response:
        return put(url=self.mockserver_server + path, headers=self.headers, json=body)
