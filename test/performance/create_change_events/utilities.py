from csv import reader
from json import load, loads
from os import getenv
from random import choice
from time import time
from typing import Any, List, Union

from boto3 import client


def setup_change_event_request() -> tuple[dict[str, str], dict[str, Any]]:
    """Setup the request headers and json payload for the change event endpoint

    Returns:
        tuple[dict[str, str], str]: Tuple containing the headers and json payload
    """
    headers = setup_headers()
    payload = load(open("resources/change_events.json", "r+"))
    payload = make_change_event_unique(payload)
    return headers, payload


def setup_headers() -> dict[str, str]:
    headers = {"sequence-number": str(round(time() * 1000))}
    api_key_json = get_secret(getenv("API_KEY_SECRET_NAME"))
    api_key = loads(api_key_json)[getenv("API_KEY_SECRET_KEY")]
    headers["x-api-key"] = api_key
    return headers


def make_change_event_unique(payload: dict[str, Any]) -> dict[str, Any]:
    """Make the change event unique by adding a unique id to the payload

    Args:
        json_payload (dict): The json payload to be modified

    Returns:
        dict: The json payload with the unique id added
    """
    payload["id"] = str(time())
    return payload


def get_secret(secret_name: str) -> str:
    sm = client(service_name="secretsmanager")
    get_secret_value_response = sm.get_secret_value(SecretId=secret_name)
    return get_secret_value_response["SecretString"]


class OdsCodes:
    invalid_ods_codes: Union[List[str], None] = None
    valid_ods_codes: Union[List[str], None] = None

    def __init__(self):
        self.valid_ods_codes = self.get_ods_codes_from_file("valid_ods_codes.csv")
        self.invalid_ods_codes = self.get_ods_codes_from_file("invalid_ods_codes.csv")

    def get_ods_codes_from_file(self, ods_code_file: str) -> list[str]:
        file = open(f"resources/{ods_code_file}", "r")
        csv_reader = reader(file)
        ods_codes = list(csv_reader)
        return ods_codes

    def get_valid_ods_code(self) -> str:
        return choice(self.valid_ods_codes)[0]

    def get_invalid_ods_code(self) -> str:
        return choice(self.invalid_ods_codes)[0]


ODSCODES = OdsCodes()
