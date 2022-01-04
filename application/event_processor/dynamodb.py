import boto3
from time import time
from os import environ

TTL = 157680000  # int((365*5)*24*60*60) . 5 years in seconds


def add_change_request_to_dynamodb(sequence_id: str, odscode: str, message: str, event_received_time: str) -> dict:
    """Add change request to dynamodb but store the message and use the event for details
    Args:
        sequence_id (str): sequence id for given ODSCode
        odscode (str): odscode
        message (str): complete message
        event_received_time (str): received timestamp from SQSEvent

    Returns:
        dict: returns response from dynamodb
    """
    event_expiry_epoch = str(int(time()) + TTL)
    dynamodb = boto3.client("dynamodb", region_name=environ["AWS_REGION"])
    response = dynamodb.put_item(
        TableName=environ["CHANGE_EVENTS_TABLE_NAME"],
        Item={
            "request_id": {"S": sequence_id},
            "ods_code": {"S": odscode},
            "message": {"S": message},
            "event_received_time": {"N": event_received_time},
            "event_expiry_epoch": {"N": event_expiry_epoch},
        },
    )
    return response
