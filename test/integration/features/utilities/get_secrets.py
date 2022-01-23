import boto3
from botocore.exceptions import ClientError
from os import getenv
from boto3 import client

def get_secret(secret_name: str) -> str:
    secrets_manager = client(service_name="secretsmanager")
    get_secret_value_response = secrets_manager.get_secret_value(SecretId=secret_name)
    return get_secret_value_response["SecretString"]

# def get_secret():

#     secret_name = getenv("API_KEY_SECRET")
#     region_name = "eu-west-2"

#     # Create a Secrets Manager client
#     session = boto3.session.Session()
#     client = session.client(service_name="secretsmanager", region_name=region_name)

#     try:
#         get_secret_value_response = client.get_secret_value(SecretId=secret_name)
#     except ClientError as e:
#         if e.response["Error"]["Code"] == "InvalidParameterException":
#             raise e
#         elif e.response["Error"]["Code"] == "InvalidRequestException":
#             raise e
#         elif e.response["Error"]["Code"] == "ResourceNotFoundException":
#             raise e
#         else:
#             raise e

#     secret = get_secret_value_response["SecretString"]
#     return secret
