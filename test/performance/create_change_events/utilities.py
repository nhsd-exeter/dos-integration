from time import time
from json import load, loads
from os import getenv

from boto3 import client


def setup_change_event_request(json_file_path: str) -> tuple[dict[str, str], str]:
    """Setup the request headers and json payload for the change event endpoint

    Args:
        json_file_path (str): Path to the json file containing the change event payload

    Returns:
        tuple[dict[str, str], str]: Tuple containing the headers and json payload
    """
    default_headers = {
        "x-api-key": None,
        "sequence-number": str(round(time() * 1000)),
    }
    api_key_json = get_secret(getenv("API_KEY_SECRET_NAME"))
    api_key = loads(api_key_json)[getenv("API_KEY_SECRET_KEY")]
    default_headers["x-api-key"] = api_key
    json_payload = load(open(json_file_path, "r+"))
    return default_headers, json_payload


def make_change_event_unique(json_payload: dict) -> dict:
    """Make the change event unique by adding a unique id to the payload

    Args:
        json_payload (dict): The json payload to be modified

    Returns:
        dict: The json payload with the unique id added
    """
    json_payload["id"] = str(time())
    return json_payload


def get_secret(secret_name: str) -> str:
    sm = client(service_name="secretsmanager")
    get_secret_value_response = sm.get_secret_value(SecretId=secret_name)
    return get_secret_value_response["SecretString"]
