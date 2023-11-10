from json import dumps
from os import getenv
from random import randint
from time import sleep
from typing import Any

from boto3 import client
from botocore import config as botocore_config
from botocore.exceptions import ConnectionClosedError
from requests import Response

cfg = botocore_config.Config(
    retries={"max_attempts": 0},
    read_timeout=900,
    connect_timeout=900,
)
LAMBDA_CLIENT_FUNCTIONS = client("lambda", config=cfg)


def invoke_dos_db_handler_lambda(lambda_payload: dict) -> Any:
    """Invoke dos db handler lambda.

    Args:
        lambda_payload (dict): Lambda payload.

    Returns:
        Any: Lambda response.
    """
    response_status = False
    response = None
    retries = 0
    while not response_status:
        try:
            response: Any = LAMBDA_CLIENT_FUNCTIONS.invoke(
                FunctionName=getenv("DOS_DB_HANDLER_LAMBDA"),
                InvocationType="RequestResponse",
                Payload=dumps(lambda_payload),
            )
            response_payload = response["Payload"].read().decode("utf-8")
            if "errorMessage" not in response_payload:
                return response_payload

            if retries > 6:
                msg = f"Unable to run test db checker lambda successfully after {retries} retries, {response_payload}"
                raise ValueError(msg)  # noqa: TRY301, RUF100

        except ConnectionClosedError:
            sleep(60)

        retries += 1
        sleep(randint(5, 15))
    return None


def invoke_quality_checker_lambda() -> Response:
    """Invoke quality checker lambda.

    Returns:
        Response: Lambda response.
    """
    return LAMBDA_CLIENT_FUNCTIONS.invoke(
        FunctionName=getenv("QUALITY_CHECKER_LAMBDA"),
        InvocationType="RequestResponse",
        Payload="{}",
    )


def re_process_payload(odscode: str, seq_number: str) -> str:
    """Reprocesses a payload from the event replay lambda.

    Args:
        odscode (str): Odscode to send to lambda
        seq_number (str): Sequence number to send to lambda

    Returns:
        str: Response from lambda
    """
    lambda_payload = {"odscode": odscode, "sequence_number": seq_number}
    response = LAMBDA_CLIENT_FUNCTIONS.invoke(
        FunctionName=getenv("EVENT_REPLAY_LAMBDA"),
        InvocationType="RequestResponse",
        Payload=dumps(lambda_payload),
    )
    return response["Payload"].read().decode("utf-8")
