import hashlib
from decimal import Decimal
from json import dumps, loads
from os import environ
from time import time
from typing import Any

from aws_lambda_powertools.logging.logger import Logger
from boto3 import client
from boto3.dynamodb.types import TypeSerializer

from common.errors import DynamoDBError

TTL = 157680000  # int((365*5)*24*60*60) 5 years in seconds
logger = Logger(child=True)
dynamodb = client("dynamodb", region_name=environ["AWS_REGION"])


def dict_hash(change_event: dict[str, Any], sequence_number: str) -> str:
    """MD5 hash of a dictionary."""
    change_event_hash = hashlib.new("md5", usedforsecurity=False)
    encoded = dumps([change_event, sequence_number], sort_keys=True).encode()
    change_event_hash.update(encoded)
    return change_event_hash.hexdigest()


def add_change_event_to_dynamodb(change_event: dict[str, Any], sequence_number: int, event_received_time: int) -> str:
    """Add change event to dynamodb but store the message and use the event for details.

    Args:
        change_event (Dict[str, Any]): sequence id for given ODSCode
        sequence_number (int): sequence id for given ODSCode
        event_received_time (str): received timestamp from SQSEvent.

    Returns:
        dict: returns response from dynamodb
    """
    record_id = dict_hash(change_event, sequence_number)
    dynamo_record = {
        "Id": record_id,
        "ODSCode": change_event["ODSCode"],
        "TTL": int(time()) + TTL,
        "EventReceived": event_received_time,
        "SequenceNumber": sequence_number,
        "Event": loads(dumps(change_event), parse_float=Decimal),
    }
    try:
        serializer = TypeSerializer()
        put_item = {k: serializer.serialize(v) for k, v in dynamo_record.items()}
        response = dynamodb.put_item(TableName=environ["CHANGE_EVENTS_TABLE_NAME"], Item=put_item)
        logger.info("Added record to dynamodb", response=response, item=put_item)
    except Exception as err:  # noqa: BLE001
        msg = f"Unable to add change event (seq no: {sequence_number}) into dynamodb"
        raise DynamoDBError(msg) from err
    return record_id


def get_latest_sequence_id_for_a_given_odscode_from_dynamodb(odscode: str) -> int:
    """Get latest sequence id for a given odscode from dynamodb.

    Args:
        odscode (str): odscode for the change event

    Returns:
        int: Sequence number of the message or None if not present.
    """
    resp = dynamodb.query(
        TableName=environ["CHANGE_EVENTS_TABLE_NAME"],
        IndexName="gsi_ods_sequence",
        KeyConditionExpression="ODSCode = :odscode",
        ExpressionAttributeValues={":odscode": {"S": odscode}},
        Limit=1,
        ScanIndexForward=False,
        ProjectionExpression="ODSCode,SequenceNumber",
    )
    sequence_number = 0
    if resp.get("Count") > 0:
        sequence_number = int(resp.get("Items")[0]["SequenceNumber"]["N"])
    logger.debug(f"Sequence number for osdscode '{odscode}'= {sequence_number}")
    return sequence_number
