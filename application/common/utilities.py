from json import dumps, loads
from os import environ, getenv
from typing import Any, Dict, Union
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from boto3 import client


logger = Logger()


def is_debug_mode() -> bool:
    """This function checks if debug mode should be enabled

    Returns:
        bool: Should debug mode be on?
    """
    return environ["PROFILE"] in ["local", "task"]


def get_environment_variable(environment_key: str) -> str:
    """This function gets an environment variable

    Args:
        message_body (str): A JSON string body
    Returns:
        Dict[str, Any]: Message body as a dictionary
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
    return getenv("MOCK_MODE", "").upper() == "TRUE"


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
    seq_num_str = record.message_attributes.get("sequence-number", {}).get("stringValue")
    return None if seq_num_str is None else int(seq_num_str)
