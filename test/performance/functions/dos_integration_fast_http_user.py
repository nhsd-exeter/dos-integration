from typing import Any

from locust import FastHttpUser

from .utilities import get_api_key


class DoSIntegrationFastHttpUser(FastHttpUser):
    """This class is to be a parent class for all DoS integration tests."""

    abstract = True
    headers: dict[str, str]
    payload: dict[str, Any]

    def on_start(self) -> None:
        """Get the api key before starting the test."""
        self.api_key = get_api_key()
