from csv import reader
from json import load, loads
from os import getenv
from random import choice
from time import time_ns
from typing import Any

from aws import get_secret
from locust import FastHttpUser


def setup_change_event_request() -> dict[str, Any]:
    """Setup the request headers and json payload for the change event endpoint."""
    with open("resources/change_event.json", "r+") as file:
        payload = load(file)
    return make_change_event_unique(payload)


def setup_headers() -> dict[str, str]:
    """Setup the headers for the change event endpoint."""
    return {"sequence-number": str(time_ns())}


def get_api_key() -> str:
    """Get the api key from AWS secrets manager."""
    api_key_json = get_secret(getenv("API_KEY_SECRET"))
    return loads(api_key_json)[getenv("NHS_UK_API_KEY")]


def make_change_event_unique(payload: dict[str, Any]) -> dict[str, Any]:
    """Make the change event unique by adding a timestamp to the address.

    Args:
        payload (dict[str, Any]): The change event payload

    Returns:
        dict[str, Any]: The change event payload with a unique address
    """
    time = time_ns()
    payload["Address1"] = f'{payload["Address1"]} {time}'
    return payload


class OdsCodes:
    """Class to get valid and invalid pharmacy ods codes."""

    invalid_ods_codes: list[list[str]] | None = None
    valid_ods_codes: list[list[str]] | None = None

    def get_ods_codes_from_file(self, ods_code_file: str) -> list[list[str]]:
        """Get the ods codes from a file.

        Args:
            ods_code_file (str): The name of the file to get the ods codes from

        Returns:
            list[list[str]]: The list of ods codes
        """
        with open(f"resources/{ods_code_file}") as file:
            csv_reader = reader(file)
            return list(csv_reader)

    def generic_get_ods_code(
        self,
        ods_code_file_name: str,
        odscode_list: list[list[str]] | None,
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
        """Get a valid pharmacy ods code.

        Returns:
            str: The valid ods code
        """
        odscode, self.valid_ods_codes = self.generic_get_ods_code("valid_ods_codes.csv", self.valid_ods_codes)
        return odscode

    def get_invalid_ods_code(self) -> str:
        """Get an invalid pharmacy ods code.

        Returns:
            str:  The invalid ods code
        """
        odscode, self.invalid_ods_codes = self.generic_get_ods_code("invalid_ods_codes.csv", self.invalid_ods_codes)
        return odscode


ODSCODES = OdsCodes()


def send_valid_change_event(change_event_class: FastHttpUser) -> FastHttpUser:
    """Send a valid change event.

    Args:
        change_event_class (FastHttpUser): The change event class

    Returns:
        FastHttpUser: The change event class
    """
    change_event_class.payload = setup_change_event_request()
    change_event_class.payload["ODSCode"] = ODSCODES.get_valid_ods_code()
    change_event_class.headers = setup_headers()
    change_event_class.headers["x-api-key"] = change_event_class.api_key
    change_event_class.client.post(
        "",
        headers=change_event_class.headers,
        json=change_event_class.payload,
        name="AllChangesChangeEvent",
    )
    return change_event_class


def send_invalid_change_event(change_event_class: FastHttpUser) -> FastHttpUser:
    """Send a valid change event.

    Args:
        change_event_class (FastHttpUser): The change event class

    Returns:
        FastHttpUser: The change event class
    """
    change_event_class.payload = setup_change_event_request()
    change_event_class.payload["ODSCode"] = ODSCODES.get_invalid_ods_code()
    change_event_class.headers = setup_headers()
    change_event_class.headers["x-api-key"] = change_event_class.api_key
    change_event_class.client.post(
        "",
        headers=change_event_class.headers,
        json=change_event_class.payload,
        name="OdscodeDoesNotExistInDoS",
    )
    return change_event_class
