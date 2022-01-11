from pytest import fixture
from os import environ
from json import dumps, loads
from decimal import Decimal
from common.dynamodb import (
    add_change_request_to_dynamodb,
    get_latest_sequence_id_for_a_given_odscode_from_dynamodb,
    dict_hash,
    TTL,
)
from boto3.dynamodb.types import TypeDeserializer
from time import time


@fixture
def dynamodb_table_create(dynamodb_client):
    """Create a DynamoDB CHANGE_EVENTS_TABLE table fixture."""
    table = dynamodb_client.create_table(
        TableName=environ["CHANGE_EVENTS_TABLE_NAME"],
        BillingMode="PAY_PER_REQUEST",
        KeySchema=[
            {"AttributeName": "Id", "KeyType": "HASH"},
            {"AttributeName": "ODSCode", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "Id", "AttributeType": "S"},
            {"AttributeName": "ODSCode", "AttributeType": "S"},
            {"AttributeName": "SequenceNumber", "AttributeType": "N"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "gsi_ods_sequence",
                "KeySchema": [
                    {"AttributeName": "ODSCode", "KeyType": "HASH"},
                    {"AttributeName": "SequenceNumber", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
    )
    return table


def test_add_change_request_to_dynamodb(dynamodb_table_create, change_event, dynamodb_client):
    # Arrange
    event_received_time = int(time())
    # Act
    change_id = dict_hash(change_event)
    response_add = add_change_request_to_dynamodb(change_event.copy(), 1, str(event_received_time))

    item = dynamodb_client.get_item(
        TableName=environ["CHANGE_EVENTS_TABLE_NAME"],
        Key={"Id": {"S": change_id}, "ODSCode": {"S": change_event["ODSCode"]}},
    )["Item"]
    deserializer = TypeDeserializer()
    deserialized = {k: deserializer.deserialize(v) for k, v in item.items()}
    expected = loads(dumps(change_event), parse_float=Decimal)

    assert response_add["ResponseMetadata"]["HTTPStatusCode"] == 200
    assert deserialized["EventReceived"] == str(event_received_time)
    assert deserialized["TTL"] == str(event_received_time + TTL)
    assert deserialized["Id"] == change_id
    assert deserialized["SequenceNumber"] == 1
    assert deserialized["Event"] == expected


def test_get_latest_sequence_id_for_a_given_odscode_from_dynamodb(dynamodb_table_create, change_event):
    event_received_time = int(time())
    add_change_request_to_dynamodb(change_event.copy(), 1, str(event_received_time))
    add_change_request_to_dynamodb(change_event.copy(), 2, str(event_received_time))
    add_change_request_to_dynamodb(change_event.copy(), 3, str(event_received_time))
    add_change_request_to_dynamodb(change_event.copy(), 4, str(event_received_time))
    add_change_request_to_dynamodb(change_event.copy(), 20, str(event_received_time))

    latest_sequence_number = get_latest_sequence_id_for_a_given_odscode_from_dynamodb(change_event["ODSCode"])
    assert latest_sequence_number == 20


def test_no_records_in_db_for_a_given_odscode(dynamodb_table_create, change_event):
    latest_sequence_number = get_latest_sequence_id_for_a_given_odscode_from_dynamodb(change_event["ODSCode"])
    assert latest_sequence_number is None
