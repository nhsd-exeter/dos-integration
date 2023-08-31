from json import dumps, loads
from os import getenv
from typing import Any

from requests import Response, post

from .aws.secrets_manager import get_secret
from .context import Context
from .utils import generate_unique_sequence_number


def process_payload(context: Context, valid_api_key: bool | None, correlation_id: str) -> Response:
    """Process payload.

    Args:
        context (Context): Test context.
        valid_api_key (bool | None): Valid api key.
        correlation_id (str): Correlation id.

    Raises:
        ValueError: Unable to process change request payload.

    Returns:
        Response: Response from the API.
    """
    api_key = "invalid"
    if valid_api_key:
        api_key = loads(get_secret(getenv("API_KEY_SECRET")))[getenv("NHS_UK_API_KEY")]
    sequence_number = generate_unique_sequence_number(context.change_event["ODSCode"])
    headers = {
        "x-api-key": api_key,
        "sequence-number": sequence_number,
        "correlation-id": correlation_id,
        "Content-Type": "application/json",
    }
    payload = context.change_event
    output = post(url=getenv("HTTPS_DOS_INTEGRATION_URL"), headers=headers, data=dumps(payload), timeout=10)
    if valid_api_key and output.status_code != 200:
        msg = f"Unable to process change request payload. Error: {output.text}"
        raise ValueError(msg)
    return output


def process_payload_with_sequence(context: Context, correlation_id: str, sequence_id: Any) -> Response:
    """Process payload with sequence.

    Args:
        context (Context): Test context.
        correlation_id (str): Correlation id.
        sequence_id (Any): Sequence id.
    """
    api_key = loads(get_secret(getenv("API_KEY_SECRET")))[getenv("NHS_UK_API_KEY")]
    headers = {
        "x-api-key": api_key,
        "correlation-id": correlation_id,
        "Content-Type": "application/json",
    }
    if sequence_id is not None:
        headers["sequence-number"] = str(sequence_id)
    payload = context.change_event
    output = post(url=getenv("HTTPS_DOS_INTEGRATION_URL"), headers=headers, data=dumps(payload), timeout=10)
    if output.status_code != 200 and isinstance(sequence_id, int):
        msg = f"Unable to process change request payload. Error: {output.text}"
        raise ValueError(msg)
    return output
