from json import loads
from os import environ
from typing import Dict

from aws_lambda_powertools import Logger
from boto3 import client

logger = Logger()



def get_secret(secret_name: str) -> Dict[str, str]:
    """Get the secret from AWS Secrets Manager

    Args:
        secret_name (str): Secret name to get

    Raises:
        e: ClientError caused by secrets manager

    Returns:
        Dict[str, str]: Secrets as a dictionary
    """
    secrets_manager = client(service_name="secretsmanager", region_name=environ["AWS_REGION"])
    secret_value_response = secrets_manager.get_secret_value(SecretId=secret_name)
    secrets_json_str = secret_value_response["SecretString"]
    secrets = loads(secrets_json_str)
    return secrets
