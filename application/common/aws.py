from json import loads
from os import environ
from typing import Dict
from aiohttp import ClientError

from aws_lambda_powertools import Logger
from boto3 import client

logger = Logger()

secrets_manager = client(service_name="secretsmanager")

def get_secret(secret_name: str) -> Dict[str, str]:
    """Get the secret from AWS Secrets Manager

    Args:
        secret_name (str): Secret name to get

    Raises:
        e: ClientError caused by secrets manager

    Returns:
        Dict[str, str]: Secrets as a dictionary
    """
    try:
        secret_value_response = secrets_manager.get_secret_value(SecretId=secret_name)
    except ClientError as err:
        raise Exception(f"Failed getting secret '{secret_name}' from secrets manager") from err
    secrets_json_str = secret_value_response["SecretString"]
    secrets = loads(secrets_json_str)
    return secrets
