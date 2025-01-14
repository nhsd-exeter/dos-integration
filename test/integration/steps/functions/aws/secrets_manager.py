from boto3 import client


def get_secret(secret_name: str) -> str:
    """Get secret from AWS Secrets Manager.

    Args:
        secret_name (str): Get secret from AWS Secrets Manager.

    Returns:
        str: Secret value.
    """
    secrets_manager = client(service_name="secretsmanager")
    get_secret_value_response = secrets_manager.get_secret_value(SecretId=secret_name)
    return get_secret_value_response["SecretString"]
