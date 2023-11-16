from decimal import Decimal
from json import dumps
from os import environ
from unittest.mock import MagicMock, patch

import pytest
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from boto3.dynamodb.types import TypeSerializer

from application.event_replay.event_replay import (
    build_correlation_id,
    get_change_event,
    lambda_handler,
    send_change_event,
    validate_event,
)

FILE_PATH = "application.event_replay.event_replay"


@pytest.fixture()
def event() -> dict[str, str]:
    return {"odscode": "FXXX1", "sequence_number": "1"}


@pytest.fixture()
def change_event():
    return {
        "Address1": "Flat 619",
        "Address2": "62 Fake Street",
        "Address3": "Hazel Grove",
        "City": "Bath",
        "County": "Somerset",
        "Postcode": "TE5 7ER",
    }


@patch.object(Logger, "append_keys")
@patch(f"{FILE_PATH}.send_change_event")
@patch(f"{FILE_PATH}.get_change_event")
@patch(f"{FILE_PATH}.build_correlation_id")
def test_lambda_handler(
    mock_build_correlation_id: MagicMock,
    mock_get_change_event: MagicMock,
    mock_send_change_event: MagicMock,
    mock_append_keys: MagicMock,
    change_event: dict[str, str],
    event: dict[str, str],
    lambda_context: LambdaContext,
):
    # Arrange
    correlation_id = "CORRELATION_ID"
    mock_build_correlation_id.return_value = correlation_id
    mock_get_change_event.return_value = change_event
    # Act
    response = lambda_handler(event, lambda_context)
    # Assert
    assert response == dumps(
        {"message": "The change event has been re-sent successfully", "correlation_id": correlation_id},
    )
    mock_append_keys.assert_any_call(ods_code=event["odscode"], sequence_number=event["sequence_number"])
    mock_build_correlation_id.assert_called_once_with()
    mock_get_change_event.assert_called_once_with(event["odscode"], Decimal(event["sequence_number"]))
    mock_send_change_event.assert_called_once_with(
        change_event,
        event["odscode"],
        int(event["sequence_number"]),
        correlation_id,
    )


def test_validate_event(event: dict[str, str]):
    # Act & Assert
    validate_event(event)


def test_validate_event_no_odscode(event: dict[str, str]):
    # Arrange
    del event["odscode"]
    # Act & Assert
    with pytest.raises(ValueError, match="odscode"):
        validate_event(event)


def test_validate_event_no_sequence_number(event: dict[str, str]):
    # Arrange
    del event["sequence_number"]
    # Act & Assert
    with pytest.raises(ValueError, match="sequence_number"):
        validate_event(event)


@patch(f"{FILE_PATH}.time_ns")
def test_build_correlation_id(mock_time_ns: MagicMock):
    # Arrange
    time = "123456789"
    mock_time_ns.return_value = time
    # Act
    response = build_correlation_id()
    # Assert
    assert response == f"{time}-local-replayed-event"


@patch(f"{FILE_PATH}.client")
def test_get_change_event(mock_client: MagicMock, change_event: dict[str, str], event: dict[str, str]):
    # Arrange
    table_name = "my-table"
    environ["CHANGE_EVENTS_TABLE_NAME"] = table_name
    environ["AWS_REGION"] = "eu-west-1"
    serializer = TypeSerializer()

    mock_client.return_value.query.return_value = {"Items": [{"Event": serializer.serialize(change_event)}]}
    # Act
    response = get_change_event(event["odscode"], Decimal(event["sequence_number"]))
    # Assert
    assert response == change_event
    mock_client.assert_called_with("dynamodb")
    mock_client().query.assert_called_with(
        TableName=table_name,
        IndexName="gsi_ods_sequence",
        ProjectionExpression="Event",
        ExpressionAttributeValues={":v1": {"S": event["odscode"]}, ":v2": {"N": event["sequence_number"]}},
        KeyConditionExpression="ODSCode = :v1 and SequenceNumber = :v2",
        Limit=1,
        ScanIndexForward=False,
    )
    # Clean up
    del environ["CHANGE_EVENTS_TABLE_NAME"]
    del environ["AWS_REGION"]


@patch(f"{FILE_PATH}.client")
def test_get_change_event_no_change_event_in_dynamodb(
    mock_client: MagicMock, change_event: dict[str, str], event: dict[str, str]
):
    # Arrange
    table_name = "my-table"
    environ["CHANGE_EVENTS_TABLE_NAME"] = table_name
    environ["AWS_REGION"] = "eu-west-1"
    mock_client.return_value.query.return_value = {"Items": []}
    # Act
    with pytest.raises(ValueError, match="No change event found for ods code FXXX1 and sequence number 1"):
        get_change_event(event["odscode"], Decimal(event["sequence_number"]))
    # Assert
    mock_client.assert_called_with("dynamodb")
    mock_client().query.assert_called_with(
        TableName=table_name,
        IndexName="gsi_ods_sequence",
        ProjectionExpression="Event",
        ExpressionAttributeValues={":v1": {"S": event["odscode"]}, ":v2": {"N": event["sequence_number"]}},
        KeyConditionExpression="ODSCode = :v1 and SequenceNumber = :v2",
        Limit=1,
        ScanIndexForward=False,
    )
    # Clean up
    del environ["CHANGE_EVENTS_TABLE_NAME"]
    del environ["AWS_REGION"]


@patch(f"{FILE_PATH}.client")
def test_send_change_event(mock_client: MagicMock, change_event: dict[str, str], event: dict[str, str]):
    # Arrange
    correlation_id = "CORRELATION_ID"
    queue_name = "my-queue"
    environ["CHANGE_EVENT_SQS_NAME"] = queue_name
    queue_url = "https://sqs.eu-west-1.amazonaws.com/123456789/my-queue"
    mock_client().get_queue_url.return_value = {"QueueUrl": queue_url}
    # Act
    send_change_event(change_event, event["odscode"], int(event["sequence_number"]), correlation_id)
    # Assert
    mock_client.assert_called_with("sqs")
    mock_client().get_queue_url.assert_called_with(QueueName=queue_name)
    mock_client().send_message.assert_called_with(
        QueueUrl=queue_url,
        MessageBody=dumps(change_event),
        MessageGroupId=event["odscode"],
        MessageAttributes={
            "correlation-id": {"StringValue": correlation_id, "DataType": "String"},
            "sequence-number": {"StringValue": str(event["sequence_number"]), "DataType": "Number"},
        },
    )
    # Clean up
    del environ["CHANGE_EVENT_SQS_NAME"]
