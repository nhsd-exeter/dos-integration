from json import load, loads
from time import sleep, time

from aws import get_secret
from locust import FastHttpUser, events, task
from utilities import total_time
from os import getenv


class NHSUKChangeEvent(FastHttpUser):
    def on_start(self):
        self.default_headers = {"Content-Type": "application/json", "x-api-key": None}
        api_key_json = get_secret(getenv("API_KEY_SECRET_NAME"))
        api_key = loads(api_key_json)[getenv("API_KEY_SECRET_KEY")]
        self.default_headers["x-api-key"] = api_key
        self.json_payload = load(open("resources/change_event.json", "r+"))

    @task
    def change_event(self):

        self.client.post(
            "/api/v1/nhsuk-event-receiver/test",
            headers=self.default_headers,
            json=self.json_payload,
        )

        self.start_time = time()
        sleep(10)  # Add receive change request here
        events.request_success.fire(
            request_type="Received", name="test", response_time=total_time(self.start_time), response_length=0
        )
