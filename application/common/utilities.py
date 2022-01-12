from json import dumps, loads
from os import environ, getenv
from typing import Any, Dict, Union

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from boto3 import client

logger = Logger(child=True)


def is_debug_mode() -> bool:
    """This function checks if debug mode should be enabled

    Returns:
        bool: Should debug mode be on?
    """
    response = False
    if environ["PROFILE"] in ["local", "task"]:
        response = True
    return response


def get_environment_variable(environment_key: str) -> str:
    """This function gets an environment variable

    Args:
        environment_key (str): [description]

    Raises:
        KeyError: If environment variable not set

    Returns:
        str: environment variable value
    """
    try:
        return environ[environment_key]
    except KeyError as e:
        logger.exception(f"Environment variable not found {environment_key}")
        raise e


def is_mock_mode() -> bool:
    """This function checks if mock mode should be enabled, default is False

    Returns:
        bool: Should mock mode be on?
    """
    if getenv("MOCK_MODE") in ["true", "True"]:
        return True
    else:
        return False


def invoke_lambda_function(lambda_name: str, lambda_event: Dict[str, Any]) -> None:
    """Invokes a lambda function with specified event

    Args:
        lambda_name (str): Name of lambda to invoke
        lambda_event (Dict[str, Any]): Event to pass to lambda
    """
    lambda_payload = dumps(lambda_event).encode("utf-8")
    lambda_client = client("lambda")
    logger.debug(f"Invoking {lambda_name}")
    lambda_client.invoke(FunctionName=lambda_name, InvocationType="Event", Payload=lambda_payload)


def extract_body(body: str) -> Dict[str, Any]:
    """Extracts the event body from the lambda function invocation event

    Args:
        message_body (str): A JSON string body
    Returns:
        Dict[str, Any]: Message body as a dictionary
    """
    try:
        body = loads(body)
    except Exception:
        logger.exception("Change Event unable to be extracted")
        raise
    return body


def get_sequence_number(record: SQSRecord) -> Union[int, None]:
    """Gets the sequence number from the SQS record

    Args:
        record (SQSRecord): SQS record

    Returns:
        Optional[int]: Sequence number of the message or None if not present
    """
    sequence_number = None
    if (
        record.message_attributes["sequence-number"] is not None
        and record.message_attributes["sequence-number"]["stringValue"] is not None
    ):
        sequence_number = int(record.message_attributes["sequence-number"]["stringValue"])
    return sequence_number
