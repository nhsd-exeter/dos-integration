from typing import Union

from locust import HttpUser, task
from utilities import setup_change_event_request, make_change_event_unique
from time import sleep


class AllChangesChangeEvent(HttpUser):
    """This class is to test a working change event"""

    weight = 3
    trace_id: Union[str, None] = None
    default_headers: Union[dict, None] = None
    payload = None

    def on_start(self):
        self.default_headers, payload = setup_change_event_request("resources/change_event_all_changes.json")
        self.payload = make_change_event_unique(payload)

    @task
    def change_event(self):
        self.client.post("", headers=self.default_headers, json=self.payload, name="AllChangesChangeEvent")
        sleep(1)


class OdscodeDoesNotExistInDoS(HttpUser):
    """This class is to test a change event with an ods code that doesn't exist in DoSs"""

    weight = 1
    trace_id: Union[str, None] = None
    default_headers: Union[dict, None] = None
    payload = None

    def on_start(self):
        self.default_headers, payload = setup_change_event_request("resources/change_event_ods_code_not_exist.json")
        self.payload = make_change_event_unique(payload)

    @task
    def change_event(self):
        self.client.post("", headers=self.default_headers, json=self.payload, name="OdscodeDoesNotExistInDoS")
        sleep(1)
