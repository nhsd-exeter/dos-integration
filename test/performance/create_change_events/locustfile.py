from typing import Any, Dict, Union

from locust import HttpUser, task
from utilities import setup_change_event_request, ODSCODES
from time import sleep


class AllChangesChangeEvent(HttpUser):
    """This class is to test a working change event"""

    weight = 3
    trace_id: Union[str, None] = None
    headers: Union[Dict[str, str], None] = None
    payload: Union[Dict[str, Any], None] = None

    def on_start(self):
        self.headers, self.payload = setup_change_event_request()
        self.payload["ODSCode"] = ODSCODES.get_valid_ods_code()

    @task
    def change_event(self):
        self.client.post("", headers=self.headers, json=self.payload, name="AllChangesChangeEvent")
        sleep(1)


class OdscodeDoesNotExistInDoS(HttpUser):
    """This class is to test a change event with an ods code that doesn't exist in DoSs"""

    weight = 1
    trace_id: Union[str, None] = None
    headers: Union[Dict[str, str], None] = None
    payload: Union[Dict[str, Any], None] = None

    def on_start(self):
        self.headers, self.payload = setup_change_event_request()
        self.payload["ODSCode"] = ODSCODES.get_invalid_ods_code()

    @task
    def change_event(self):
        self.client.post("", headers=self.headers, json=self.payload, name="OdscodeDoesNotExistInDoS")
        sleep(1)
