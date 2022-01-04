from pytest import fixture
from os import environ
from dynamodb import add_change_request_to_dynamodb, TTL
from time import time


@fixture
def dynamodb_table_create(dynamodb_client):
    """Create a DynamoDB CHANGE_EVENTS_TABLE table fixture."""
    table = dynamodb_client.create_table(
        TableName=environ["CHANGE_EVENTS_TABLE_NAME"],
        BillingMode="PAY_PER_REQUEST",
        KeySchema=[
            {"AttributeName": "request_id", "KeyType": "HASH"},
            {"AttributeName": "ods_code", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "request_id", "AttributeType": "S"},
            {"AttributeName": "ods_code", "AttributeType": "S"},
        ],
    )
    return table


def test_add_change_request_to_dynamodb(dynamodb_table_create, dynamodb_client):
    # Arrange
    sequence_id = "3"
    odscode = "FX111"
    message = "TEST  MESSAGE"
    event_received_time = int(time())
    # Act
    response_add = add_change_request_to_dynamodb(sequence_id, odscode, message, str(event_received_time))
    response_query = dynamodb_client.query(
        TableName=environ["CHANGE_EVENTS_TABLE_NAME"],
        KeyConditionExpression="request_id =:request_id AND ods_code = :ods_code",
        ExpressionAttributeValues={":request_id": {"S": sequence_id}, ":ods_code": {"S": odscode}},
    )
    items = response_query["Items"]
    # Assert
    assert response_add["ResponseMetadata"]["HTTPStatusCode"] == 200
    assert items[0]["message"]["S"] == "TEST  MESSAGE"
    assert items[0]["event_received_time"]["N"] == str(event_received_time)
    assert items[0]["event_expiry_epoch"]["N"] == str(event_received_time + TTL)
    assert len(items) == 1
