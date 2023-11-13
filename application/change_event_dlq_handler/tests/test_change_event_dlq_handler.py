from json import dumps
from os import environ
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from aws_embedded_metrics.logger.metrics_logger import MetricsLogger

from application.change_event_dlq_handler.change_event_dlq_handler import lambda_handler
from application.conftest import PHARMACY_STANDARD_EVENT, PHARMACY_STANDARD_EVENT_STAFF

FILE_PATH = "application.change_event_dlq_handler.change_event_dlq_handler"

CHANGE_EVENT_FROM_CHANGE_EVENT_QUEUE = PHARMACY_STANDARD_EVENT.copy()
CHANGE_EVENT_FROM_HOLDING_QUEUE = {
    "change_event": CHANGE_EVENT_FROM_CHANGE_EVENT_QUEUE,
    "dynamo_record_id": "123456789",
    "message_received": "2021-01-01T00:00:00.000000Z",
    "sequence_number": "123456789",
    "correlation_id": "123456789",
}

STAFF_CHANGE_EVENT_FROM_CHANGE_EVENT_QUEUE = PHARMACY_STANDARD_EVENT_STAFF.copy()
STAFF_CHANGE_EVENT_FROM_HOLDING_QUEUE = {
    "change_event": STAFF_CHANGE_EVENT_FROM_CHANGE_EVENT_QUEUE,
    "dynamo_record_id": "123456789",
    "message_received": "2021-01-01T00:00:00.000000Z",
    "sequence_number": "123456789",
    "correlation_id": "123456789",
}


@pytest.fixture()
def dead_letter_change_event_from_change_event_queue():
    return {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy0a...",
                "body": dumps(CHANGE_EVENT_FROM_CHANGE_EVENT_QUEUE),
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1545082649183",
                    "SenderId": "AIDAIENQZJOLO23YVJ4VO",
                    "ApproximateFirstReceiveTimestamp": "1545082649185",
                },
                "messageAttributes": {
                    "correlation-id": {
                        "stringValue": "059f36b4-87a3-44ab-83d2-661975830a7d",
                        "stringListValues": [],
                        "binaryListValues": [],
                        "dataType": "String",
                    },
                    "sequence-number": {
                        "stringValue": "123456789",
                        "stringListValues": [],
                        "binaryListValues": [],
                        "dataType": "String",
                    },
                },
                "md5OfBody": "e4e68fb7bd0e697a0ae8f1bb342846b3",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:my-queue",
                "awsRegion": "us-east-2",
            },
        ],
    }


@pytest.fixture()
def dead_letter_staff_change_event_from_change_event_queue():
    return {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy0a...",
                "body": dumps(STAFF_CHANGE_EVENT_FROM_CHANGE_EVENT_QUEUE),
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1545082649183",
                    "SenderId": "AIDAIENQZJOLO23YVJ4VO",
                    "ApproximateFirstReceiveTimestamp": "1545082649185",
                },
                "messageAttributes": {
                    "correlation-id": {
                        "stringValue": "059f36b4-87a3-44ab-83d2-661975830a7d",
                        "stringListValues": [],
                        "binaryListValues": [],
                        "dataType": "String",
                    },
                    "sequence-number": {
                        "stringValue": "123456789",
                        "stringListValues": [],
                        "binaryListValues": [],
                        "dataType": "String",
                    },
                },
                "md5OfBody": "e4e68fb7bd0e697a0ae8f1bb342846b3",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:my-queue",
                "awsRegion": "us-east-2",
            },
        ],
    }


@pytest.fixture()
def dead_letter_change_event_from_holding_queue():
    return {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy0a...",
                "body": dumps(CHANGE_EVENT_FROM_HOLDING_QUEUE),
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1545082649183",
                    "SenderId": "AIDAIENQZJOLO23YVJ4VO",
                    "ApproximateFirstReceiveTimestamp": "1545082649185",
                },
                "messageAttributes": {},
                "md5OfBody": "e4e68fb7bd0e697a0ae8f1bb342846b3",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:my-queue",
                "awsRegion": "us-east-2",
            },
        ],
    }


@patch(f"{FILE_PATH}.extract_body")
@patch(f"{FILE_PATH}.add_change_event_to_dynamodb")
@patch.object(MetricsLogger, "put_metric")
@patch.object(MetricsLogger, "set_dimensions")
def test_lambda_handler_event_from_change_event_queue(
    mock_put_metric: MagicMock,
    mock_set_dimensions: MagicMock,
    mock_add_change_event_to_dynamodb: MagicMock,
    mock_extract_body: MagicMock,
    dead_letter_staff_change_event_from_change_event_queue: dict[str, Any],
    dead_letter_change_event_from_change_event_queue: dict[str, Any],
    lambda_context,
):
    # Arrange
    environ["ENV"] = "local"
    mock_extract_body.return_value = extracted_body = "Test message1."
    # Act
    assert "Staff" in dead_letter_staff_change_event_from_change_event_queue["Records"][0]["body"]
    lambda_handler(dead_letter_staff_change_event_from_change_event_queue, lambda_context)
    # Assert
    mock_extract_body.assert_called_once_with(dead_letter_change_event_from_change_event_queue["Records"][0]["body"])
    expected_timestamp = int(
        dead_letter_change_event_from_change_event_queue["Records"][0]["attributes"]["SentTimestamp"],
    )
    mock_add_change_event_to_dynamodb.assert_called_once_with(extracted_body, 123456789, expected_timestamp)
    # Clean up
    del environ["ENV"]


@patch(f"{FILE_PATH}.add_change_event_to_dynamodb")
@patch.object(MetricsLogger, "put_metric")
@patch.object(MetricsLogger, "set_dimensions")
def test_lambda_handler_event_from_holding_queue(
    mock_put_metric: MagicMock,
    mock_set_dimensions: MagicMock,
    mock_add_change_event_to_dynamodb: MagicMock,
    dead_letter_change_event_from_holding_queue: dict[str, Any],
    lambda_context,
):
    # Arrange
    environ["ENV"] = "local"
    # Act
    lambda_handler(dead_letter_change_event_from_holding_queue, lambda_context)
    # Assert
    expected_timestamp = int(dead_letter_change_event_from_holding_queue["Records"][0]["attributes"]["SentTimestamp"])
    mock_add_change_event_to_dynamodb.assert_called_once_with(
        CHANGE_EVENT_FROM_CHANGE_EVENT_QUEUE,
        CHANGE_EVENT_FROM_HOLDING_QUEUE["sequence_number"],
        expected_timestamp,
    )
    # Clean up
    del environ["ENV"]
