from csv import reader
from json import load, loads
from os import getenv
from random import choice
from time import time_ns
from typing import Any

from aws import get_secret


def setup_change_event_request() -> dict[str, Any]:
    """Setup the request headers and json payload for the change event endpoint."""
    payload = load(open("resources/change_event.json", "r+"))
    payload = make_change_event_unique(payload)
    return payload


def setup_headers() -> dict[str, str]:
    return {"sequence-number": str(time_ns())}


def get_api_key() -> str:
    api_key_json = get_secret(getenv("API_KEY_SECRET_NAME"))
    return loads(api_key_json)[getenv("API_KEY_SECRET_KEY")]


def make_change_event_unique(payload: dict[str, Any]) -> dict[str, Any]:
    time = time_ns()
    payload["Address1"] = f'{payload["Address1"]} {time}'
    return payload


class OdsCodes:
    invalid_ods_codes: list[list[str]] | None = None
    valid_ods_codes: list[list[str]] | None = None

    def get_ods_codes_from_file(self, ods_code_file: str) -> list[list[str]]:
        file = open(f"resources/{ods_code_file}")
        csv_reader = reader(file)
        return list(csv_reader)

    def generic_get_ods_code(
        self, ods_code_file_name: str, odscode_list: list[list[str]] | None,
    ) -> tuple[str, list[list[str]]]:
        """Get a random ods code from list or file if list is empty.

        Args:
            ods_code_file_name (str): The name of the file to get the ods codes from if the list is empty
            odscode_list (Optional[list[list[str]]]): The list of ods codes to get the odscode from

        Returns:
            Tuple[str, list[list[str]]]: The odscode and the list of ods codes
        """
        if odscode_list is None or len(odscode_list) == 0:
            odscode_list = self.get_ods_codes_from_file(ods_code_file_name)
        odscode_list_of_one = choice(odscode_list)
        odscode_list.remove(odscode_list_of_one)
        return odscode_list_of_one[0], odscode_list

    def get_valid_ods_code(self) -> str:
        odscode, self.valid_ods_codes = self.generic_get_ods_code("valid_ods_codes.csv", self.valid_ods_codes)
        return odscode

    def get_invalid_ods_code(self) -> str:
        odscode, self.invalid_ods_codes = self.generic_get_ods_code("invalid_ods_codes.csv", self.invalid_ods_codes)
        return odscode


ODSCODES = OdsCodes()


def send_valid_change_event(change_event_class):
    change_event_class.payload = setup_change_event_request()
    change_event_class.payload["ODSCode"] = ODSCODES.get_valid_ods_code()
    change_event_class.headers = setup_headers()
    change_event_class.headers["x-api-key"] = change_event_class.api_key
    change_event_class.client.post(
        "", headers=change_event_class.headers, json=change_event_class.payload, name="AllChangesChangeEvent",
    )
    return change_event_class


def send_invalid_change_event(change_event_class):
    change_event_class.payload = setup_change_event_request()
    change_event_class.payload["ODSCode"] = ODSCODES.get_invalid_ods_code()
    change_event_class.headers = setup_headers()
    change_event_class.headers["x-api-key"] = change_event_class.api_key
    change_event_class.client.post(
        "", headers=change_event_class.headers, json=change_event_class.payload, name="OdscodeDoesNotExistInDoS",
    )
    return change_event_class
