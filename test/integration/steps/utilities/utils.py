import random
from ast import literal_eval
from decimal import Decimal
from json import dumps, loads
from os import getenv
from time import time_ns
from typing import Any, Dict

import requests
from boto3 import client
from boto3.dynamodb.types import TypeDeserializer
from requests import Response

from .get_secrets import get_secret

URL = getenv("URL")
CR_URL = getenv("CR_URL")
SQS_URL = getenv("SQS_URL")
EVENT_PROCESSOR = getenv("EVENT_PROCESSOR")
DYNAMO_DB_TABLE = getenv("DYNAMO_DB_TABLE")
LAMBDA_CLIENT_FUNCTIONS = client("lambda")
SQS_CLIENT = client("sqs")
DYNAMO_CLIENT = client("dynamodb")
RDS_DB_CLIENT = client("rds")


def process_payload(payload: dict, valid_api_key: bool, correlation_id: str) -> Response:
    api_key = "invalid"
    if valid_api_key:
        api_key = loads(get_secret(getenv("API_KEY_SECRET")))[getenv("NHS_UK_API_KEY")]
    sequence_number = str(time_ns())
    headers = {
        "x-api-key": api_key,
        "sequence-number": sequence_number,
        "correlation-id": correlation_id,
        "Content-Type": "application/json",
    }
    payload["Unique_key"] = generate_random_int()
    output = requests.request("POST", URL, headers=headers, data=dumps(payload))
    return output


def process_change_request_payload(payload: dict, api_key_valid: bool) -> Response:
    api_key = "invalid"
    if api_key_valid:
        secret = loads(get_secret(getenv("CR_API_KEY_SECRET")))
        api_key = secret[getenv("CR_API_KEY_KEY")]
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }
    output = requests.request("POST", CR_URL, headers=headers, data=dumps(payload))
    return output


def debug_purge_queue():
    try:
        SQS_CLIENT.purge_queue(QueueUrl=SQS_URL)
    except Exception as e:
        print(f"ERROR!..UNABLE TO PURGE. {e}")


def get_stored_events_from_dynamo_db(odscode: str, sequence_number: Decimal) -> dict:
    print(f"{DYNAMO_DB_TABLE} {odscode} {sequence_number}")
    resp = DYNAMO_CLIENT.query(
        TableName=DYNAMO_DB_TABLE,
        IndexName="gsi_ods_sequence",
        ProjectionExpression="ODSCode,SequenceNumber",
        ExpressionAttributeValues={
            ":v1": {
                "S": odscode,
            },
            ":v2": {
                "N": str(sequence_number),
            },
        },
        KeyConditionExpression="ODSCode = :v1 and SequenceNumber = :v2 ",
        Limit=1,
        ScanIndexForward=False,
    )
    item = resp["Items"][0]
    deserializer = TypeDeserializer()
    deserialized = {k: deserializer.deserialize(v) for k, v in item.items()}
    return deserialized


def get_lambda_info(info_param: str) -> str:
    values = {"state": "State", "status": "LastUpdateStatus", "description": "Description"}
    param = values[info_param]
    response = LAMBDA_CLIENT_FUNCTIONS.get_function(FunctionName=EVENT_PROCESSOR)
    return response["Configuration"][param]


def get_latest_sequence_id_for_a_given_odscode(odscode: str) -> int:
    """Get latest sequence id for a given odscode from dynamodb"""
    try:
        resp = DYNAMO_CLIENT.query(
            TableName=DYNAMO_DB_TABLE,
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
        print(f"Unable to get sequence id from dynamodb for a given ODSCode {odscode} {DYNAMO_DB_TABLE} .Error: {err}")
        raise
    return sequence_number


def generate_unique_sequence_number(odscode: str) -> str:
    return str(get_latest_sequence_id_for_a_given_odscode(odscode) + 1)


def generate_random_int() -> str:
    return str(random.sample(range(1000), 1)[0])


def get_odscodes_list() -> list[list[str]]:
    lambda_payload = {"type": "get_odscodes"}
    response = invoke_test_db_checker_handler_lambda(lambda_payload)
    data = loads(response["Payload"].read().decode("utf-8"))
    data = literal_eval(data)
    return data


def get_changes(correlation_id: str) -> list:
    lambda_payload = {"type": "get_changes", "correlation_id": correlation_id}
    response = invoke_test_db_checker_handler_lambda(lambda_payload)
    data = loads(response["Payload"].read().decode("utf-8"))
    data = literal_eval(data)
    return data


def get_change_event_demographics(odscode: str) -> Dict[str, Any]:
    lambda_payload = {"type": "change_event_demographics", "odscode": odscode}
    response = invoke_test_db_checker_handler_lambda(lambda_payload)
    data = loads(response["Payload"].read().decode("utf-8"))
    # data = literal_eval(data)
    data = dict(data)
    return data


def get_change_event_standard_opening_times(service_id: str) -> Any:
    lambda_payload = {"type": "change_event_standard_opening_times", "service_id": service_id}
    response = invoke_test_db_checker_handler_lambda(lambda_payload)
    data = loads(response["Payload"].read().decode("utf-8"))
    data = literal_eval(data)
    return data


def get_change_event_specified_opening_times(service_id: str) -> Any:
    lambda_payload = {"type": "change_event_specified_opening_times", "service_id": service_id}
    response = invoke_test_db_checker_handler_lambda(lambda_payload)
    data = loads(response["Payload"].read().decode("utf-8"))
    data = literal_eval(data)
    return data


def invoke_test_db_checker_handler_lambda(lambda_payload: dict) -> Any:
    response: Any = LAMBDA_CLIENT_FUNCTIONS.invoke(
        FunctionName=getenv("TEST_DB_CHECKER_FUNCTION_NAME"),
        InvocationType="RequestResponse",
        Payload=dumps(lambda_payload),
    )
    return response


def generate_correlation_id(suffix=None) -> str:
    name_no_space = getenv("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0].replace(" ", "_")
    run_id = getenv("RUN_ID")
    correlation_id = f"{run_id}_{name_no_space}" if suffix is None else f"{run_id}_{suffix}"
    correlation_id = (
        correlation_id if len(correlation_id) < 100 else correlation_id[:99]
    )  # DoS API Gateway max reference is 100 characters
    return correlation_id


def re_process_payload(odscode: str, seq_number: str) -> str:
    lambda_payload = {"odscode": odscode, "sequence_number": seq_number}
    response = LAMBDA_CLIENT_FUNCTIONS.invoke(
        FunctionName=getenv("EVENT_REPLAY"),
        InvocationType="RequestResponse",
        Payload=dumps(lambda_payload),
    )
    print(response)
    return response
