import boto3
from json import dumps, loads
import hashlib
from decimal import Decimal
from typing import Any, Dict
from boto3.dynamodb.types import TypeSerializer
from time import time
from os import environ
from aws_lambda_powertools.logging.logger import Logger

TTL = 157680000  # int((365*5)*24*60*60) . 5 years in seconds
logger = Logger(child=True)


def dict_hash(change_event: Dict[str, Any], sequence_number: str) -> str:
    """MD5 hash of a dictionary."""
    change_event_hash = hashlib.md5()
    encoded = dumps([change_event, sequence_number], sort_keys=True).encode()
    change_event_hash.update(encoded)
    return change_event_hash.hexdigest()


def add_change_request_to_dynamodb(
    change_event: Dict[str, Any], sequence_number: int, event_received_time: str
) -> dict:
    """Add change request to dynamodb but store the message and use the event for details
    Args:
        change_event (Dict[str, Any]): sequence id for given ODSCode
        event_received_time (str): received timestamp from SQSEvent

    Returns:
        dict: returns response from dynamodb
    """
    dynamo_record = {
        "Id": dict_hash(change_event, sequence_number),
        "ODSCode": change_event["ODSCode"],
        "TTL": str(int(time()) + TTL),
        "EventReceived": event_received_time,
        "SequenceNumber": sequence_number,
        "Event": loads(dumps(change_event), parse_float=Decimal),
    }
    try:
        dynamodb = boto3.client("dynamodb", region_name=environ["AWS_REGION"])
        serializer = TypeSerializer()
        put_item = {k: serializer.serialize(v) for k, v in dynamo_record.items()}
        response = dynamodb.put_item(TableName=environ["CHANGE_EVENTS_TABLE_NAME"], Item=put_item)
        logger.info(f"Added record to dynamodb. {put_item}")
    except Exception as err:
        logger.exception(f"Unable to insert a record into dynamodb.Error: {err}")
        raise
    return response


def get_latest_sequence_id_for_a_given_odscode_from_dynamodb(odscode: str) -> int:

    """Get latest sequence id for a given odscode from dynamodb
    Args:
        odscode (str): odscode for the change event
    Returns:
        int: Sequence number of the message or None if not present
    """
    try:
        dynamodb = boto3.client("dynamodb", region_name=environ["AWS_REGION"])
        resp = dynamodb.query(
            TableName=environ["CHANGE_EVENTS_TABLE_NAME"],
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
        logger.exception(f"Unable to get sequence id from dynamodb for a given ODSCode {odscode} .Error: {err}")
        raise
    return sequence_number
