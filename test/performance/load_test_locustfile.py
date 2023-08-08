from typing import Any

from locust import FastHttpUser, constant_pacing, task
from utilities import get_api_key, send_invalid_change_event, send_valid_change_event


class AllChangesChangeEvent(FastHttpUser):
    """This class is to test a working change event."""

    weight = 9
    trace_id: str | None = None
    headers: dict[str, str] | None = None
    payload: dict[str, Any] | None = None
    wait_time = constant_pacing(10)

    def on_start(self) -> None:
        """Get the api key before starting the test."""
        self.api_key = get_api_key()

    @task
    def change_event(self) -> None:
        """Send a change event."""
        self = send_valid_change_event(self)


class OdscodeDoesNotExistInDoS(FastHttpUser):
    """This class is to test a change event with an ods code that doesn't exist in DoS."""

    weight = 1
    trace_id: str | None = None
    headers: dict[str, str] | None = None
    payload: dict[str, Any] | None = None
    wait_time = constant_pacing(10)

    def on_start(self) -> None:
        """Get the api key before starting the test."""
        self.api_key = get_api_key()

    @task
    def change_event(self) -> None:
        """Send a change event."""
        self = send_invalid_change_event(self)
