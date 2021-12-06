from base64 import b64encode
from os import getenv
from typing import Any, Dict

from json import loads
from aws_lambda_powertools.utilities.typing import LambdaContext
from boto3 import client


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """Entrypoint handler for the authoriser lambda

    Args:
        event (Dict[str, Any]): Lambda function invocation event
        context (LambdaContext): Lambda function context object

    Returns:
        dict: Policy to allow connection to the API Gateway Mock
    """
    try:
        basic_auth = get_basic_auth()
        assert event["authorizationToken"] == basic_auth, "Invalid credentials"
    except Exception as e:
        print(f"Authentication method failed with error: {e}")
        return generate_policy(None, "Deny", event["methodArn"])
    return generate_policy("*", "Allow", event["methodArn"])


def get_basic_auth() -> str:
    """Get basic auth credentials from environment variables

    Returns:
        str: Basic auth credentials
    """
    sm = client("secretsmanager")
    secret_string = sm.get_secret_value(SecretId=getenv("DOS_API_GATEWAY_CREDENTIALS_SECRET_NAME"))["SecretString"]
    secret_dict = loads(secret_string)
    username_key = getenv("DOS_API_GATEWAY_USERNAME_KEY")
    password_key = getenv("DOS_API_GATEWAY_PASSWORD_KEY")
    username = secret_dict[username_key]
    password = secret_dict[password_key]
    encoded_credentials = b64encode(bytes(f"{username}:{password}", encoding="utf-8")).decode("utf-8")
    return f"Basic {encoded_credentials}"


def generate_policy(principal_id: Any, effect: str, method_arn: str) -> Dict[str, Any]:
    """Generates policy to allow/deny connection to the DoS API Gateway Mock

    Args:
        principal_id (str|None): Principal ID for Policy
        effect (str): Effect for Policy (Allow or Deny)
        method_arn (str): Method Arn for Resource

    Returns:
        dict: Policy to allow/deny connection to the DoS API Gateway Mock
    """
    auth_response = {}
    auth_response["principalId"] = principal_id
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {"Sid": "FirstStatement", "Action": "execute-api:Invoke", "Effect": effect, "Resource": method_arn}
        ],
    }
    auth_response["policyDocument"] = policy_document
    return auth_response
