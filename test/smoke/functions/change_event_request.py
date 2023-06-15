from json import dumps, loads
from os import getenv
from time import time_ns

from requests import Response, post

from .aws import get_latest_sequence_id_for_a_given_odscode, get_secret


def send_change_event(change_event_json: dict) -> Response:
    """Send change event to DoS Integration API.

    Args:
        change_event_json (dict): The change event to send
    """
    api_key = loads(get_secret(getenv("API_KEY_SECRET")))[getenv("NHS_UK_API_KEY")]
    sequence_number = generate_unique_sequence_number(change_event_json["ODSCode"])
    correlation_id = f"{time_ns()}-Smoke-Test"
    api_gateway_url = getenv("HTTPS_DOS_INTEGRATION_URL")
    headers = {
        "x-api-key": api_key,
        "sequence-number": sequence_number,
        "correlation-id": correlation_id,
        "Content-Type": "application/json",
    }
    response = post(url=api_gateway_url, headers=headers, data=dumps(change_event_json), timeout=10)
    if response.status_code != 200:
        msg = f"Unable to process change request payload. Error: {response.text}"
        raise ValueError(msg)
    return response


def generate_unique_sequence_number(odscode: str) -> str:
    """Generate unique sequence number.

    Args:
        odscode (str): ODSCode.

    Returns:
        str: Unique sequence number.
    """
    return str(get_latest_sequence_id_for_a_given_odscode(odscode) + 1)
