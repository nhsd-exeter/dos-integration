import requests
import json
from os import getenv
from features.utilities.get_secrets import get_secret
from json import dumps
from boto3 import client
from time import sleep
from boto3.dynamodb.types import TypeDeserializer
from decimal import Decimal
import boto3
import psycopg2
from psycopg2.extras import DictCursor

URL = getenv("URL")
SQS_URL = getenv("SQS_URL")
EVENT_PROCESSOR = getenv("EVENT_PROCESSOR")
DYNAMO_DB_TABLE = getenv("DYNAMO_DB_TABLE")
LAMBDA_CLIENT_FUNCTIONS = client("lambda")
SQS_CLIENT = client("sqs")
DYNAMO_CLIENT = client("dynamodb")
DYNAMODB = boto3.resource("dynamodb")
RDS_DB_CLIENT = client("rds")


def process_payload(payload: dict) -> str:
    sequence_no = generate_unique_int(payload["ODSCode"])
    headers = {
        "x-api-key": json.loads(get_secret(getenv("API_KEY_SECRET")))[getenv("NHS_UK_API_KEY")],
        "sequence-number": sequence_no,
        "Content-Type": "application/json",
    }
    payload["Address1"] = sequence_no + " MANSFIELD ROAD"
    output = requests.request("POST", URL, headers=headers, data=dumps(payload))
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
            ':v1': {
                'S': odscode,
            },
            ':v2': {
                'N': str(sequence_number),
            },
        },
        KeyConditionExpression='ODSCode = :v1 and SequenceNumber = :v2 ',
        Limit=1,
        ScanIndexForward=False,
    )
    item = resp["Items"][0]
    deserializer = TypeDeserializer()
    deserialized = {k: deserializer.deserialize(v) for k, v in item.items()}
    return deserialized


def get_response(payload: str) -> str:
    response = process_payload(payload)
    return response.json()["message"]


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


def generate_unique_int(odscode: str) -> str:
    return str(get_latest_sequence_id_for_a_given_odscode(odscode) + 1)


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
