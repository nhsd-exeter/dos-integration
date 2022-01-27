from typing import Any, Dict, Union

from locust import FastHttpUser, task, constant_pacing
from utilities import setup_change_event_request, ODSCODES, setup_headers, get_api_key


class AllChangesChangeEvent(FastHttpUser):
    """This class is to test a working change event"""

    weight = 9
    trace_id: Union[str, None] = None
    headers: Union[Dict[str, str], None] = None
    payload: Union[Dict[str, Any], None] = None
    wait_time = constant_pacing(30)

    def on_start(self):
        self.api_key = get_api_key()

    @task
    def change_event(self):
        self.payload = setup_change_event_request()
        self.payload["ODSCode"] = ODSCODES.get_valid_ods_code()
        self.headers = setup_headers(self.payload["ODSCode"])
        self.headers["x-api-key"] = self.api_key
        self.client.post("", headers=self.headers, json=self.payload, name="AllChangesChangeEvent")


class OdscodeDoesNotExistInDoS(FastHttpUser):
    """This class is to test a change event with an ods code that doesn't exist in DoS"""

    weight = 1
    trace_id: Union[str, None] = None
    headers: Union[Dict[str, str], None] = None
    payload: Union[Dict[str, Any], None] = None
    wait_time = constant_pacing(30)

    def on_start(self):
        self.api_key = get_api_key()

    @task
    def change_event(self):
        self.payload = setup_change_event_request()
        self.payload["ODSCode"] = ODSCODES.get_invalid_ods_code()
        self.headers = setup_headers(self.payload["ODSCode"])
        self.headers["x-api-key"] = self.api_key
        self.client.post("", headers=self.headers, json=self.payload, name="OdscodeDoesNotExistInDoS")
