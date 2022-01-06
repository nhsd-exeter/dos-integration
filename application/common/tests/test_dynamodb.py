from pytest import fixture
from os import environ
from json import dumps, loads
from decimal import Decimal
from common.dynamodb import add_change_request_to_dynamodb, dict_hash, TTL
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
        ],
    )
    return table


def test_add_change_request_to_dynamodb(dynamodb_table_create, change_event, dynamodb_client):
    # Arrange
    event_received_time = int(time())
    # Act
    change_id = dict_hash(change_event)
    response_add = add_change_request_to_dynamodb(change_event.copy(),1, str(event_received_time))

    item = dynamodb_client.get_item(
        TableName=environ["CHANGE_EVENTS_TABLE_NAME"], Key={"Id": {"S": change_id}, "ODSCode": {"S": change_event["ODSCode"]}}
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
