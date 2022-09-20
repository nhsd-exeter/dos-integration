from csv import reader
from json import load, loads
from os import getenv
from random import choice
from time import time_ns
from typing import Any, Union

from aws import get_secret


def setup_change_event_request() -> dict[str, Any]:
    """Setup the request headers and json payload for the change event endpoint"""
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
    invalid_ods_codes: Union[list[list[str]], None] = None
    valid_ods_codes: Union[list[list[str]], None] = None

    def get_ods_codes_from_file(self, ods_code_file: str) -> list[list[str]]:
        file = open(f"resources/{ods_code_file}", "r")
        csv_reader = reader(file)
        return list(csv_reader)

    def get_valid_ods_code(self) -> str:
        if self.valid_ods_codes is None or len(self.valid_ods_codes) == 0:
            self.valid_ods_codes = self.get_ods_codes_from_file("valid_ods_codes.csv")
        odscode_list_of_one = choice(self.valid_ods_codes)
        self.valid_ods_codes.remove(odscode_list_of_one)
        return odscode_list_of_one[0]

    def get_invalid_ods_code(self) -> str:
        if self.invalid_ods_codes is None or len(self.invalid_ods_codes) == 0:
            self.invalid_ods_codes = self.get_ods_codes_from_file("invalid_ods_codes.csv")
        odscode_list_of_one = choice(self.invalid_ods_codes)
        self.invalid_ods_codes.remove(odscode_list_of_one)
        return odscode_list_of_one[0]


ODSCODES = OdsCodes()
