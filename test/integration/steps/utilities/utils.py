import json
import random
from decimal import Decimal
from json import dumps
from os import getenv
from time import sleep, time_ns

import psycopg2
import requests
from boto3 import client
from boto3.dynamodb.types import TypeDeserializer
from psycopg2.extras import DictCursor
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
        api_key = json.loads(get_secret(getenv("API_KEY_SECRET")))[getenv("NHS_UK_API_KEY")]
    sequence_number = str(time_ns())
    headers = {
        "x-api-key": api_key,
        "sequence-number": sequence_number,
        "correlation-id": correlation_id,
        "Content-Type": "application/json",
    }
    payload["Address1"] = generate_random_int() + " MANSFIELD ROAD"
    output = requests.request("POST", URL, headers=headers, data=dumps(payload))
    return output


def process_change_request_payload(payload: dict, api_key_valid: bool) -> Response:
    api_key = "invalid"
    if api_key_valid:
        secret = json.loads(get_secret(getenv("CR_API_KEY_SECRET")))
        api_key = secret[getenv("CR_API_KEY_KEY")]

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }

    print(CR_URL)
    output = requests.request("POST", CR_URL, headers=headers, data=dumps(payload))
    print(output)
    return output


def debug_purge_queue():
    try:
        SQS_CLIENT.purge_queue(QueueUrl=SQS_URL)
    except Exception as e:
        print(f"ERROR!..UNABLE TO PURGE. {e}")


def get_stored_events_from_dynamo_db(odscode: str, sequence_number: Decimal) -> dict:
    print(f"{DYNAMO_DB_TABLE} {odscode} {sequence_number}")
    sleep(5)
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
        print(f"Unable to get sequence id from dynamodb for a given ODSCode {odscode} { DYNAMO_DB_TABLE} .Error: {err}")
        raise
    return sequence_number


def generate_unique_sequence_number(odscode: str) -> str:
    return str(get_latest_sequence_id_for_a_given_odscode(odscode) + 1)


def generate_random_int() -> str:
    return str(random.sample(range(1000), 1)[0])


def search_dos_db(query: str) -> list:
    db_username = json.loads(get_secret(getenv("DOS_DB_USERNAME_SECRET_NAME")))[getenv("DOS_DB_USERNAME_KEY")]
    db_password = json.loads(get_secret(getenv("DOS_DB_PASSWORD_SECRET_NAME")))[getenv("DOS_DB_PASSWORD_KEY")]
    sleep(5)
    response = RDS_DB_CLIENT.describe_db_instances(DBInstanceIdentifier=getenv("DOS_DB_IDENTIFIER_NAME"))
    server_url = response["DBInstances"][0]["Endpoint"]["Address"]
    db_connection = psycopg2.connect(
        host=server_url,
        port="5432",
        dbname="pathwaysdos_regressiondi",
        user=db_username,
        password=db_password,
        connect_timeout=30,
        options="-c search_path=dbo,pathwaysdos",
    )
    db_cursor = db_connection.cursor(cursor_factory=DictCursor)
    db_cursor.execute(query)
    rows = db_cursor.fetchall()
    db_cursor.close()
    return rows


def generate_correlation_id(suffix=None) -> str:
    name_no_space = getenv("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0].replace(" ", "_")
    run_id = getenv("RUN_ID")
    correlation_id = f"{run_id}_{name_no_space}" if suffix is None else f"{run_id}_{suffix}"
    correlation_id = (
        correlation_id if len(correlation_id) < 100 else correlation_id[:99]
    )  # DoS API Gateway max reference is 100 characters
    return correlation_id
