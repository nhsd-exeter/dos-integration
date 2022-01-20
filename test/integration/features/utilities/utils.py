import requests
import json
from os import getenv
from features.utilities.get_secrets import get_secret
from json import load, dumps
from boto3 import client
from time import sleep
from decimal import Decimal
import boto3
from boto3.dynamodb.conditions import Attr

url = getenv("URL")
SQS_URL = getenv("SQS_URL")
event_processor = getenv("EVENT_PROCESSOR")
dynamo_db_table = getenv("DYNAMO_DB_TABLE")
lambda_client_functions = client("lambda")
sqs_client = client("sqs")
dynamo_client = client("dynamodb")
dynamodb = boto3.resource("dynamodb")


def process_payload(payload: dict) -> str:
    headers = {
        "x-api-key": json.loads(get_secret())[getenv("NHS_UK_API_KEY")],
        "sequence-number": str(get_new_sequence_id_for_a_given_odscode(payload["ODSCode"])),
        "Content-Type": "application/json",
    }
    output = requests.request("POST", url, headers=headers, data=dumps(payload))
    sleep(30)
    return output


def debug_purge_queue():
    try:
        sqs_client.purge_queue(QueueUrl=SQS_URL)
    except Exception as e:
        print(f"ERROR!..UNABLE TO PURGE. {e}")


def get_stored_events_from_db(seq_id: str) -> dict:
    table = dynamodb.Table(dynamo_db_table)
    sequence_number = seq_id
    response = table.scan(FilterExpression=Attr("SequenceNumber").eq(Decimal(sequence_number)))
    items = response["Items"]
    for item in items:
        return item
    # return json.loads(items, indent=2, default=str)


def get_response(payload: str, corr_id: str) -> str:
    payload_name = payload
    correlation_id = corr_id
    response = process_change_event(payload_name, correlation_id)
    return response.json()["message"]


# This matches a payload file with a string describing it from the Steps


def get_payload(payload_name: str) -> str:
    values = {"valid": "11_expected_schema.json", "invalid": "10_invalid.json"}
    if payload_name in ["valid", "invalid"]:
        payload_file_name = values[payload_name]
    else:
        raise Exception("Unable to find Payload by request name")
    with open(f"./features/resources/payloads/{payload_file_name}", "r", encoding="utf-8") as json_file:
        return dumps(load(json_file))


def get_lambda_info(info_param: str) -> str:
    values = {"state": "State", "status": "LastUpdateStatus", "description": "Description"}
    param = values[info_param]
    response = lambda_client_functions.get_function(FunctionName=event_processor)
    return response["Configuration"][param]


def get_new_sequence_id_for_a_given_odscode(odscode: str) -> int:
    # Get latest sequence id for a given odscode from dynamodb
    try:
        resp = dynamo_client.query(
            TableName=dynamo_db_table,
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
        print(f"Unable to get sequence id from dynamodb for a given ODSCode {odscode} .Error: {err}")
        raise
    return sequence_number + 1
