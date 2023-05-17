import hashlib
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from itertools import count
from json import dumps, loads
from os import environ
from time import time
from typing import Any

from aws_lambda_powertools.logging.logger import Logger
from boto3 import client, resource
from boto3.dynamodb.types import TypeSerializer

from common.errors import DynamoDBError

TTL = 157680000  # int((365*5)*24*60*60) 5 years in seconds
logger = Logger(child=True)
dynamodb = client("dynamodb", region_name=environ["AWS_REGION"])
ddb_resource = resource("dynamodb", region_name=environ["AWS_REGION"])


def dict_hash(change_event: dict[str, Any], sequence_number: str) -> str:
    """MD5 hash of a dictionary."""
    change_event_hash = hashlib.new("md5", usedforsecurity=False)
    encoded = dumps([change_event, sequence_number], sort_keys=True).encode()
    change_event_hash.update(encoded)
    return change_event_hash.hexdigest()


def put_circuit_is_open(circuit: str, is_open: bool) -> None:
    """Set the circuit open status for a given circuit.

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
    except Exception as err:  # noqa: BLE001
        msg = f"Unable to set circuit '{circuit}' to open."
        raise DynamoDBError(msg) from err


def get_circuit_is_open(circuit: str) -> bool | None:
    """Gets the open status of a given circuit.

    Args:
        circuit (str): Name of the circuit

    Returns:
        Union[bool, None]: returns the status or None if the circuit does not exist.
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

    except Exception as err:  # noqa: BLE001
        msg = f"Unable to get circuit status for '{circuit}'."
        raise DynamoDBError(msg) from err


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
        logger.info("Added record to dynamodb", extra={"response": response, "item": put_item})
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


def get_newest_event_per_odscode(threads: int = 2, limit: int = None) -> dict[str, dict]:
    """Will return a dict map of the most recent DB entry for every ODSCode."""
    change_event_table = ddb_resource.Table(environ["CHANGE_EVENTS_TABLE_NAME"])
    logger.info(
        f"Returning newest events per ODSCode from DDB table "
        f"{environ['CHANGE_EVENTS_TABLE_NAME']}' ({threads} threads).",
    )

    def merge_newest_events(newest_events: dict, more_events: list[dict]):  # noqa: ANN202
        for event in more_events:
            newest_event = newest_events.get(event["ODSCode"])
            if not (newest_event is not None and newest_event["SequenceNumber"] > event["SequenceNumber"]):
                newest_events[event["ODSCode"]] = event

    def scan_thread(segment: int, total_segments: int):  # noqa: ANN202
        scan_kwargs = {"Segment": segment, "TotalSegments": total_segments}
        if limit is not None:
            scan_kwargs["Limit"] = limit
        newest_events = {}
        total_events = 0
        for scans in count():
            resp = change_event_table.scan(**scan_kwargs)
            more_events = resp["Items"]
            total_events += len(more_events)
            merge_newest_events(newest_events, more_events)
            if "LastEvaluatedKey" not in resp or scans % 10 == 0:
                logger.info(f"Thread {segment} found {len(newest_events)}/{total_events} unique ODSCode events")
            if "LastEvaluatedKey" in resp:
                scan_kwargs["ExclusiveStartKey"] = resp["LastEvaluatedKey"]
            else:
                return newest_events
        return None

    with ThreadPoolExecutor() as executor:
        thread_runs = [executor.submit(scan_thread, segment=i, total_segments=threads) for i in range(threads)]
        newest_events = {}
        for thread in thread_runs:
            merge_newest_events(newest_events, thread.result().values())
    return newest_events
