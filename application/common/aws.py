from json import loads
from os import getenv
from typing import Dict

from aws_lambda_powertools import Logger
from boto3 import client
from botocore.exceptions import ClientError

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
    sm = client(service_name="secretsmanager", region_name=getenv("AWS_REGION"))
    try:
        get_secret_value_response = sm.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        logger.exception(f"Failed getting secret {secret_name}")
        raise e
    else:
        secrets = get_secret_value_response["SecretString"]
        secrets = loads(secrets)
        return secrets
