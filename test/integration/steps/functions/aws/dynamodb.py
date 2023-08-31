from decimal import Decimal
from os import getenv

from boto3 import client
from boto3.dynamodb.types import TypeDeserializer

DYNAMO_DB_TABLE = getenv("DYNAMO_DB_TABLE")
DYNAMO_CLIENT = client("dynamodb")


def get_stored_events_from_dynamo_db(odscode: str, sequence_number: Decimal) -> dict:
    """Get stored events from dynamodb.

    Args:
        odscode (str): ODSCode.
        sequence_number (Decimal): Sequence number.

    Raises:
        ValueError: No event found in dynamodb for ODSCode {odscode} and SequenceNumber {sequence_number}.

    Returns:
        dict: Stored events from dynamodb.
    """
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
        KeyConditionExpression="ODSCode = :v1 and SequenceNumber = :v2",
        Limit=1,
        ScanIndexForward=False,
    )
    if len(resp["Items"]) == 0:
        msg = f"No event found in dynamodb for ODSCode {odscode} and SequenceNumber {sequence_number}"
        raise ValueError(msg)
    item = resp["Items"][0]
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in item.items()}


def get_latest_sequence_id_for_a_given_odscode(odscode: str) -> int:
    """Get latest sequence id for a given odscode from dynamodb.

    Args:
        odscode (str): ODSCode.

    Raises:
        Exception: Unable to get sequence id from dynamodb

    Returns:
        int: Latest sequence id for a given odscode from dynamodb.
    """
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
