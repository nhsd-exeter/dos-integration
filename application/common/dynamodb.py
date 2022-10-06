import hashlib
from decimal import Decimal
from json import dumps, loads
from os import environ
from time import time
from typing import Any, Dict, Union, List, Optional

from aws_lambda_powertools.logging.logger import Logger
from boto3 import client, resource
from boto3.dynamodb.types import TypeSerializer

from common.errors import DynamoDBException

TTL = 157680000  # int((365*5)*24*60*60) 5 years in seconds
logger = Logger(child=True)
dynamodb = client("dynamodb", region_name=environ["AWS_REGION"])
ddb_change_table = resource("dynamodb").Table(environ["CHANGE_EVENTS_TABLE_NAME"])


def dict_hash(change_event: Dict[str, Any], sequence_number: str) -> str:
    """MD5 hash of a dictionary."""
    change_event_hash = hashlib.new("md5", usedforsecurity=False)
    encoded = dumps([change_event, sequence_number], sort_keys=True).encode()
    change_event_hash.update(encoded)
    return change_event_hash.hexdigest()


def put_circuit_is_open(circuit: str, is_open: bool) -> None:
    """Set the circuit open status for a given circuit

    Args:
        circuit (str): Name of the circuit
        is_open (bool): boolean as to whether the circuit is open/True (broken) or closed/False (ok)
    """
    dynamo_record = {
        "Id": circuit,
        "ODSCode": "CIRCUIT",
        "IsOpen": is_open,
    }
    try:
        serializer = TypeSerializer()
        put_item = {k: serializer.serialize(v) for k, v in dynamo_record.items()}
        response = dynamodb.put_item(TableName=environ["CHANGE_EVENTS_TABLE_NAME"], Item=put_item)
        logger.info("Put circuit status", extra={"response": response, "item": put_item})
    except Exception as err:
        raise DynamoDBException(f"Unable to set circuit '{circuit}' to open.") from err


def get_circuit_is_open(circuit: str) -> Union[bool, None]:
    """Gets the open status of a given circuit
    Args:
        circuit (str): Name of the circuit
    Returns:
        Union[bool, None]: returns the status or None if the circuit does not exist
    """
    try:
        respone = dynamodb.get_item(
            TableName=environ["CHANGE_EVENTS_TABLE_NAME"],
            Key={
                "Id": {
                    "S": circuit,
                },
                "ODSCode": {
                    "S": "CIRCUIT",
                },
            },
        )
        item = respone.get("Item")
        logger.debug(f"Circuit '{circuit}' is_open resp={item}")
        return None if item is None else bool(item["IsOpen"]["BOOL"])

    except Exception as err:
        raise DynamoDBException(f"Unable to get circuit status for '{circuit}'.") from err


def add_change_event_to_dynamodb(change_event: Dict[str, Any], sequence_number: int, event_received_time: int) -> str:
    """Add change event to dynamodb but store the message and use the event for details
    Args:
        change_event (Dict[str, Any]): sequence id for given ODSCode
        event_received_time (str): received timestamp from SQSEvent

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
        logger.info("Added record to dynamodb", extra={"response": response, "item": put_item})
    except Exception as err:
        raise DynamoDBException(f"Unable to add change event (seq no: {sequence_number}) into dynamodb") from err
    return record_id


def get_latest_sequence_id_for_a_given_odscode_from_dynamodb(odscode: str) -> int:
    """Get latest sequence id for a given odscode from dynamodb
    Args:
        odscode (str): odscode for the change event
    Returns:
        int: Sequence number of the message or None if not present
    """
    try:
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
    except Exception as err:
        raise DynamoDBException(f"Unable to get sequence id from dynamodb for a given ODSCode '{odscode}'.") from err
    return sequence_number


def get_most_recent_events(max_pages: Optional[int] = None) -> List[dict]:
    # Get all items from DDB
    resp = ddb_change_table.scan()
    data = resp.get("Items")
    pages = 1
    while "LastEvaluatedKey" in resp and (max_pages is None or pages < max_pages):
        logger.info(f"Received {pages} page/s of DDB Table data.")
        resp = ddb_change_table.scan(ExclusiveStartKey=resp["LastEvaluatedKey"])
        data.extend(resp["Items"])
        pages += 1
    
    # Find the most recent entry of each odscode present
    most_recent_events = {}
    for item in data:
        odscode = item["ODSCode"]
        try:
            if most_recent_events[odscode]["SequenceNumber"] < item["SequenceNumber"]:
                most_recent_events[odscode] = item
        except KeyError:
            most_recent_events[odscode] = item

    return most_recent_events
