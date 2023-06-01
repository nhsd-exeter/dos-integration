from json import loads

from aws_lambda_powertools.logging import Logger
from boto3 import client
from botocore.exceptions import ClientError

logger = Logger()

secrets_manager = client(service_name="secretsmanager")


def get_secret(secret_name: str) -> dict[str, str]:
    """Get the secret from AWS Secrets Manager.

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
        msg = f"Failed getting secret '{secret_name}' from secrets manager"
        raise Exception(msg) from err  # noqa: TRY002
    secrets_json_str = secret_value_response["SecretString"]
    return loads(secrets_json_str)
