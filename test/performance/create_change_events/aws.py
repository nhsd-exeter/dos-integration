from boto3 import client


def get_secret(secret_name: str) -> str:
    sm = client(service_name="secretsmanager")
    get_secret_value_response = sm.get_secret_value(SecretId=secret_name)
    return get_secret_value_response["SecretString"]
