import boto3
from json import dumps, loads
import hashlib
from decimal import Decimal
from typing import Any, Dict, Union
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


def put_circuit_is_open(circuit: str, is_open: bool) -> None:
    """Set the circuit open status for a given circuit
    Args:
        circuit (str): Name of the circuit
        is_open (bool): boolean as to whether the circuit is open (broken) or closed

    Returns:
        None
    """
    try:
        dynamodb = boto3.client("dynamodb")
        dynamo_record = {
            "Id": circuit,
            "ODSCode": "CIRCUIT",
            "IsOpen": is_open,
        }
        serializer = TypeSerializer()
        put_item = {k: serializer.serialize(v) for k, v in dynamo_record.items()}
        response = dynamodb.put_item(TableName=environ["CHANGE_EVENTS_TABLE_NAME"], Item=put_item)
        logger.info("Put circuit status", extra={"response": response, "item": put_item})
    except Exception as err:
        raise Exception("Unable to insert a record into dynamodb.") from err 


def get_circuit_is_open(circuit: str) -> Union[bool, None]:
    """Gets the open status of a given circuit
    Args:
        circuit (str): Name of the circuit
    Returns:
        Union[bool, None]: returns the status or None if the circuit does not exist
    """
    try:
        dynamodb = boto3.client("dynamodb")
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
        if item is None:
            return None
        else:
            return int(item["IsOpen"]["BOOL"])
    except Exception as err:
        raise Exception(f"Unable to get circuit status for {circuit}", str(err)) from err


def add_change_request_to_dynamodb(change_event: Dict[str, Any], sequence_number: int, event_received_time: int) -> str:
    """Add change request to dynamodb but store the message and use the event for details
    Args:
        change_event (Dict[str, Any]): sequence id for given ODSCode
        event_received_time (str): received timestamp from SQSEvent

    Returns:
        dict: returns response from dynamodb
    """
    try:
        dynamodb = boto3.client("dynamodb")
        record_id = dict_hash(change_event, sequence_number)
        dynamo_record = {
            "Id": record_id,
            "ODSCode": change_event["ODSCode"],
            "TTL": int(time()) + TTL,
            "EventReceived": event_received_time,
            "SequenceNumber": sequence_number,
            "Event": loads(dumps(change_event), parse_float=Decimal),
        }
        serializer = TypeSerializer()
        put_item = {k: serializer.serialize(v) for k, v in dynamo_record.items()}
        response = dynamodb.put_item(TableName=environ["CHANGE_EVENTS_TABLE_NAME"], Item=put_item)
        logger.info("Added record to dynamodb", extra={"response": response, "item": put_item})
        return record_id
    except Exception as err:
        raise Exception(f"Unable to insert a record into dynamodb") from err



def get_latest_sequence_id_for_a_given_odscode_from_dynamodb(odscode: str) -> int:
    """Get latest sequence id for a given odscode from dynamodb
    Args:
        odscode (str): odscode for the change event
    Returns:
        int: Sequence number of the message or None if not present
    """
    try:
        dynamodb = boto3.client("dynamodb")
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
        return sequence_number
    except Exception as err:
        raise Exception(f"Unable to get sequence id from dynamodb for a given ODSCode {odscode}") from err
