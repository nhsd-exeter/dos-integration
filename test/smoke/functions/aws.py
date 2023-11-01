from json import dumps
from os import getenv
from time import sleep

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


def get_latest_sequence_id_for_a_given_odscode(odscode: str) -> int:
    """Get latest sequence id for a given odscode from dynamodb.

    Args:
        odscode (str): ODSCode.

    Raises:
        Exception: Unable to get sequence id from dynamodb

    Returns:
        int: Latest sequence id for a given odscode from dynamodb.
    """
    dynamodb_client = client(service_name="dynamodb")
    dynamodb_table = getenv("DYNAMO_DB_TABLE")
    try:
        resp = dynamodb_client.query(
            TableName=dynamodb_table,
            IndexName="gsi_ods_sequence",
            KeyConditionExpression="ODSCode = :odscode",
            ExpressionAttributeValues={
                ":odscode": {"S": odscode},
            },
            Limit=1,
            ScanIndexForward=False,
            ProjectionExpression="ODSCode,SequenceNumber",
        )
        sequence_number = 0
        if resp.get("Count") > 0:
            sequence_number = int(resp.get("Items")[0]["SequenceNumber"]["N"])
    except Exception as err:
        print(f"Unable to get sequence id from dynamodb for a given ODSCode {odscode} {dynamodb_table} .Error: {err}")
        raise
    return sequence_number


def invoke_dos_db_handler_lambda(lambda_payload: dict) -> str:
    """Invoke dos db handler lambda.

    Args:
        lambda_payload (dict): Lambda payload.

    Returns:
        str: Lambda response payload (json).
    """
    lambda_client = client("lambda")
    response_status = False
    response = None
    retries = 0
    while not response_status:
        response = lambda_client.invoke(
            FunctionName=getenv("DOS_DB_HANDLER_LAMBDA_NAME"),
            InvocationType="RequestResponse",
            Payload=dumps(lambda_payload),
        )
        response_payload = response["Payload"].read().decode("utf-8")
        if "errorMessage" not in response_payload:
            return response_payload

        if retries > 6:
            msg = f"Unable to run DoS db handler lambda successfully after {retries} retries: {response_payload}"
            raise ValueError(msg)
        retries += 1
        sleep(10)
    return response
