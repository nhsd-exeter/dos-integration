from base64 import b64encode
from os import getenv


def lambda_handler(event, context):
    """Entrypoint handler for the authoriser lambda

    Args:
        event (Dict[str, Any]): Lambda function invocation event
        context (LambdaContext): Lambda function context object

    """
    print(event)
    try:

        basic_auth = get_basic_auth()
        print(basic_auth)
        print(event["authorizationToken"])
        assert event["authorizationToken"] == basic_auth, "Invalid credentials"
    except Exception as e:
        print(f"Authentication method failed with error: {e}")
        return generatePolicy(None, "Deny", event["methodArn"])
    return generatePolicy("*", "Allow", event["methodArn"])


def get_basic_auth():
    username = getenv("DOS_API_GATEWAY_USERNAME")
    password = getenv("DOS_API_GATEWAY_PASSWORD")
    encoded_credentials = b64encode(bytes(f"{username}:{password}", encoding="utf-8")).decode("utf-8")
    return f"Basic {encoded_credentials}"


def generatePolicy(principalId, effect, methodArn):
    authResponse = {}
    authResponse["principalId"] = principalId

    if effect and methodArn:
        policyDocument = {
            "Version": "2012-10-17",
            "Statement": [
                {"Sid": "FirstStatement", "Action": "execute-api:Invoke", "Effect": effect, "Resource": methodArn}
            ],
        }

        authResponse["policyDocument"] = policyDocument

    return authResponse
