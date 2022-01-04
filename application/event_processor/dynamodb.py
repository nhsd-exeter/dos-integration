import boto3
from json import dumps, loads
import hashlib
from decimal import Decimal
from typing import Any, Dict
from boto3.dynamodb.types import TypeSerializer
from time import time
from os import environ

TTL = 157680000  # int((365*5)*24*60*60) . 5 years in seconds


def dict_hash(change_event: Dict[str, Any]) -> str:
    """MD5 hash of a dictionary."""
    change_event_hash = hashlib.md5()
    encoded = dumps(change_event, sort_keys=True).encode()
    change_event_hash.update(encoded)
    return change_event_hash.hexdigest()


def add_change_request_to_dynamodb(change_event: Dict[str, Any], event_received_time: str) -> dict:
    """Add change request to dynamodb but store the message and use the event for details
    Args:
        change_event (Dict[str, Any]): sequence id for given ODSCode
        event_received_time (str): received timestamp from SQSEvent

    Returns:
        dict: returns response from dynamodb
    """
    change_event["Id"] = dict_hash(change_event)
    change_event["TTL"] = str(int(time()) + TTL)
    change_event["EventReceived"] = event_received_time
    change_event = loads(dumps(change_event), parse_float=Decimal)
    dynamodb = boto3.client("dynamodb", region_name=environ["AWS_REGION"])
    serializer = TypeSerializer()
    put_item = {k: serializer.serialize(v) for k, v in change_event.items()}
    response = dynamodb.put_item(
        TableName=environ["CHANGE_EVENTS_TABLE_NAME"],
        Item=put_item,
    )
    return response
