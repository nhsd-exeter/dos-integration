from json import dumps
import base64
from os import environ, getenv
from typing import Any, Dict

from aws_lambda_powertools import Logger
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
    """[summary]

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
    lambda_event["correlation_id"] = logger.get_correlation_id()
    lambda_payload = dumps(lambda_event).encode("utf-8")
    lambda_client = client("lambda")
    logger.debug(f"Invoking {lambda_name}")
    lambda_client.invoke(FunctionName=lambda_name, InvocationType="Event", Payload=lambda_payload)
