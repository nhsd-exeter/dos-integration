from typing import Union

from locust import HttpUser, task
from utilities import setup_change_event_request, make_change_event_unique
from time import sleep


class AllChangesChangeEvent(HttpUser):
    """This class is to test a working change event"""

    weight = 3
    trace_id: Union[str, None] = None
    default_headers: Union[dict, None] = None
    json_payload = None

    def on_start(self):
        self.default_headers, json_payload = setup_change_event_request("resources/change_event_all_changes.json")
        self.json_payload = make_change_event_unique(json_payload)

    @task
    def change_event(self):
        self.client.post("", headers=self.default_headers, json=self.json_payload, name="AllChangesChangeEvent")
        sleep(1)

class NoChangesChangeEvent(HttpUser):
    """This class is to test a working change event"""

    weight = 1
    trace_id: Union[str, None] = None
    default_headers: Union[dict, None] = None
    json_payload = None

    def on_start(self):
        self.default_headers, json_payload = setup_change_event_request("resources/change_event_all_changes.json")
        self.json_payload = make_change_event_unique(json_payload)

    @task
    def change_event(self):
        self.client.post("", headers=self.default_headers, json=self.json_payload, name="AllChangesChangeEvent")
        sleep(1)


class WrongODSCodeChangeEvent(HttpUser):
    """This class is to test a change event with an ods code that doesn't exist in DoSs"""

    weight = 1
    trace_id: Union[str, None] = None
    default_headers: Union[dict, None] = None
    json_payload = None

    def on_start(self):
        self.default_headers, json_payload = setup_change_event_request(
            "resources/change_event_ods_code_not_exist.json"
        )
        self.json_payload = make_change_event_unique(json_payload)

    @task
    def change_event(self):
        self.client.post("", headers=self.default_headers, json=self.json_payload, name="WrongODSCodeChangeEvent")
        sleep(1)
