from typing import Any

from locust import FastHttpUser, task
from utilities import get_api_key, send_invalid_change_event, send_valid_change_event


class AllChangesChangeEvent(FastHttpUser):
    """This class is to test a working change event."""

    weight = 19
    trace_id: str | None = None
    headers: dict[str, str] | None = None
    payload: dict[str, Any] | None = None

    def on_start(self):
        self.api_key = get_api_key()

    @task
    def change_event(self):
        self = send_valid_change_event(self)


class OdscodeDoesNotExistInDoS(FastHttpUser):
    """This class is to test a change event with an ods code that doesn't exist in DoS."""

    weight = 1
    trace_id: str | None = None
    headers: dict[str, str] | None = None
    payload: dict[str, Any] | None = None

    def on_start(self):
        self.api_key = get_api_key()

    @task
    def change_event(self):
        self = send_invalid_change_event(self)
