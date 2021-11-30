from os import getenv

from boto3 import client
from requests.auth import HTTPBasicAuth

sm = client("secretsmanager")


def lambda_handler(event, context):
    """Entrypoint handler for the authoriser lambda

    Args:
        event (Dict[str, Any]): Lambda function invocation event
        context (LambdaContext): Lambda function context object

    """

    response = {"isAuthorized": False}
    try:
        basic_auth = get_basic_auth()
        if event["headers"]["Authorization"] == basic_auth:
            response = {"isAuthorized": True}
    except Exception as e:
        print(f"Authentication method failed with error: {e}")
    print(f"Response: {response}")
    return response


def get_basic_auth():
    return HTTPBasicAuth(
        getenv("DOS_API_GATEWAY_USERNAME"),
        getenv("DOS_API_GATEWAY_PASSWORD"),
    )
