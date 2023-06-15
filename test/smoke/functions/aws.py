from json import dumps
from os import getenv
from time import sleep

from boto3 import client


def invoke_dos_db_handler_lambda(lambda_payload: dict) -> str:
    """Invoke dos db handler lambda.

    Args:
        lambda_payload (dict): Lambda payload.

    Returns:
        str: Lambda response payload (json).
    """
    lambda_client = client("lambda")
    response_status = False
    response = None
    retries = 0
    while not response_status:
        response = lambda_client.invoke(
            FunctionName=getenv("DOS_DB_HANDLER_LAMBDA_NAME"),
            InvocationType="RequestResponse",
            Payload=dumps(lambda_payload),
        )
        response_payload = response["Payload"].read().decode("utf-8")
        if "errorMessage" not in response_payload:
            return response_payload

        if retries > 6:
            msg = f"Unable to run test db checker lambda successfully after {retries} retries"
            raise ValueError(msg)
        retries += 1
        sleep(10)
    return response
