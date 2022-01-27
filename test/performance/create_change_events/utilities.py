from csv import reader
from json import load, loads
from os import getenv
from random import choice, randint
from time import time_ns
from typing import Any, Union

from aws import get_secret


def setup_change_event_request() -> dict[str, Any]:
    """Setup the request headers and json payload for the change event endpoint"""
    payload = load(open("resources/change_events.json", "r+"))
    payload = make_change_event_unique(payload)
    return payload


def setup_headers(ods_code: str) -> dict[str, str]:
    headers = {"sequence-number": str(time_ns())}
    return headers


def get_api_key() -> str:
    api_key_json = get_secret(getenv("API_KEY_SECRET_NAME"))
    api_key = loads(api_key_json)[getenv("API_KEY_SECRET_KEY")]
    return api_key


def make_change_event_unique(payload: dict[str, Any]) -> dict[str, Any]:
    payload["OrganisationName"] = f'{payload["OrganisationName"]} {randint(0, 10000000)}'
    return payload


class OdsCodes:
    invalid_ods_codes: Union[list[list[str]], None] = None
    valid_ods_codes: Union[list[list[str]], None] = None

    def __init__(self):
        self.valid_ods_codes = self.get_ods_codes_from_file("valid_ods_codes.csv")
        self.invalid_ods_codes = self.get_ods_codes_from_file("invalid_ods_codes.csv")

    def get_ods_codes_from_file(self, ods_code_file: str) -> list[list[str]]:
        file = open(f"resources/{ods_code_file}", "r")
        csv_reader = reader(file)
        ods_codes = list(csv_reader)
        return ods_codes

    def get_valid_ods_code(self) -> str:
        return choice(self.valid_ods_codes)[0]

    def get_invalid_ods_code(self) -> str:
        return choice(self.invalid_ods_codes)[0]


ODSCODES = OdsCodes()
