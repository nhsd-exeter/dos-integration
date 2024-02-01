from decimal import Decimal
from json import dumps, loads
from os import environ
from time import time
from unittest.mock import MagicMock, patch

from aws_lambda_powertools.logging import Logger
from boto3.dynamodb.types import TypeDeserializer

FILE_PATH = "application.common.dynamodb"


def test_add_change_event_to_dynamodb(
    dynamodb_table_create: dict[str, str], change_event: dict[str, str], dynamodb_client: object
) -> None:
    from application.common.dynamodb import TTL, add_change_event_to_dynamodb, dict_hash

    # Arrange
    event_received_time = int(time())
    # Act
    sequence_number = 1
    change_id = dict_hash(change_event, sequence_number)
    response_id = add_change_event_to_dynamodb(change_event.copy(), sequence_number, event_received_time)

    item = dynamodb_client.get_item(
        TableName=environ["CHANGE_EVENTS_TABLE_NAME"],
        Key={"Id": {"S": change_id}, "ODSCode": {"S": change_event["ODSCode"]}},
    )["Item"]
    deserializer = TypeDeserializer()
    deserialized = {k: deserializer.deserialize(v) for k, v in item.items()}
    expected = loads(dumps(change_event), parse_float=Decimal)

    assert response_id == change_id
    assert deserialized["EventReceived"] == event_received_time
    assert deserialized["TTL"] == int(event_received_time + TTL)
    assert deserialized["Id"] == change_id
    assert deserialized["SequenceNumber"] == 1
    assert deserialized["Event"] == expected


def test_get_latest_sequence_id_for_same_change_event_from_dynamodb(
    dynamodb_table_create: dict[str, str], change_event: dict[str, str], dynamodb_client: object
) -> None:
    from application.common.dynamodb import (
        add_change_event_to_dynamodb,
        get_latest_sequence_id_for_a_given_odscode_from_dynamodb,
    )

    event_received_time = int(time())
    add_change_event_to_dynamodb(change_event.copy(), 20, event_received_time)
    add_change_event_to_dynamodb(change_event.copy(), 1, event_received_time)
    add_change_event_to_dynamodb(change_event.copy(), 2, event_received_time)
    add_change_event_to_dynamodb(change_event.copy(), 3, event_received_time)
    add_change_event_to_dynamodb(change_event.copy(), 4, event_received_time)

    resp = dynamodb_client.query(
        TableName=environ["CHANGE_EVENTS_TABLE_NAME"],
        IndexName="gsi_ods_sequence",
        KeyConditionExpression="ODSCode = :odscode",
        ExpressionAttributeValues={
            ":odscode": {"S": change_event["ODSCode"]},
        },
        ScanIndexForward=False,
    )
    assert resp.get("Count") == 5
    latest_sequence_number = get_latest_sequence_id_for_a_given_odscode_from_dynamodb(change_event["ODSCode"])
    assert latest_sequence_number == 20


def test_same_sequence_id_and_same_change_event_multiple_times(
    dynamodb_table_create: dict[str, str], change_event: dict[str, str], dynamodb_client: object
) -> None:
    from application.common.dynamodb import (
        add_change_event_to_dynamodb,
        get_latest_sequence_id_for_a_given_odscode_from_dynamodb,
    )

    event_received_time = int(time())
    add_change_event_to_dynamodb(change_event.copy(), 3, event_received_time)
    add_change_event_to_dynamodb(change_event.copy(), 3, event_received_time)
    add_change_event_to_dynamodb(change_event.copy(), 3, event_received_time)
    add_change_event_to_dynamodb(change_event.copy(), 3, event_received_time)
    resp = dynamodb_client.query(
        TableName=environ["CHANGE_EVENTS_TABLE_NAME"],
        IndexName="gsi_ods_sequence",
        KeyConditionExpression="ODSCode = :odscode",
        ExpressionAttributeValues={
            ":odscode": {"S": change_event["ODSCode"]},
        },
        ScanIndexForward=False,
    )
    assert resp.get("Count") == 1
    latest_sequence_number = get_latest_sequence_id_for_a_given_odscode_from_dynamodb(change_event["ODSCode"])
    assert latest_sequence_number == 3


def test_no_records_in_db_for_a_given_odscode(dynamodb_table_create: object, change_event: dict[str, str]) -> None:
    from application.common.dynamodb import get_latest_sequence_id_for_a_given_odscode_from_dynamodb

    latest_sequence_number = get_latest_sequence_id_for_a_given_odscode_from_dynamodb(change_event["ODSCode"])
    assert latest_sequence_number == 0


@patch.object(Logger, "error")
def test_get_latest_sequence_id_for_different_change_event_from_dynamodb(
    mock_logger: MagicMock,
    dynamodb_table_create: object,
    change_event: dict[str, str],
    dynamodb_client: object,
) -> None:
    from application.common.dynamodb import (
        add_change_event_to_dynamodb,
        get_latest_sequence_id_for_a_given_odscode_from_dynamodb,
    )

    event_received_time = int(time())
    odscode = change_event["ODSCode"]
    new_change_event = change_event.copy()
    add_change_event_to_dynamodb(new_change_event, 44, event_received_time)
    add_change_event_to_dynamodb(copy_and_modify_website(new_change_event, "www.test1.com"), 1, event_received_time)
    add_change_event_to_dynamodb(copy_and_modify_website(new_change_event, "www.test2.com"), 2, event_received_time)
    add_change_event_to_dynamodb(copy_and_modify_website(new_change_event, "www.test3.com"), 3, event_received_time)
    add_change_event_to_dynamodb(copy_and_modify_website(new_change_event, "www.test4.com"), 4, event_received_time)
    resp = dynamodb_client.query(
        TableName=environ["CHANGE_EVENTS_TABLE_NAME"],
        IndexName="gsi_ods_sequence",
        KeyConditionExpression="ODSCode = :odscode",
        ExpressionAttributeValues={
            ":odscode": {"S": odscode},
        },
        ScanIndexForward=False,
        ProjectionExpression="ODSCode,SequenceNumber",
    )
    expected_latest_sequence_number = 44
    expected_count = 5
    expected_items = [
        {
            "ODSCode": {
                "S": "TES73",
            },
            "SequenceNumber": {
                "N": "44",
            },
        },
        {
            "ODSCode": {
                "S": "TES73",
            },
            "SequenceNumber": {
                "N": "4",
            },
        },
        {
            "ODSCode": {
                "S": "TES73",
            },
            "SequenceNumber": {
                "N": "3",
            },
        },
        {
            "ODSCode": {
                "S": "TES73",
            },
            "SequenceNumber": {
                "N": "2",
            },
        },
        {
            "ODSCode": {
                "S": "TES73",
            },
            "SequenceNumber": {
                "N": "1",
            },
        },
    ]
    assert resp.get("Items") == expected_items
    assert resp.get("Count") == expected_count
    latest_sequence_number = get_latest_sequence_id_for_a_given_odscode_from_dynamodb(odscode)
    assert latest_sequence_number == expected_latest_sequence_number


def copy_and_modify_website(change_event: dict[str, str], new_website: str) -> None:
    copy = change_event.copy()
    copy["Contacts"][0]["ContactValue"] = new_website
    return copy
