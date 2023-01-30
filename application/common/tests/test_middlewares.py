import logging
from json import dumps

from aws_lambda_powertools.utilities.data_classes import SQSEvent
from botocore.exceptions import ClientError
from pytest import raises

from ..middlewares import (
    redact_staff_key_from_event,
    unhandled_exception_logging,
    unhandled_exception_logging_hidden_event,
)
from ..utilities import extract_body
from .conftest import PHARMACY_STANDARD_EVENT, PHARMACY_STANDARD_EVENT_STAFF


def test_redact_staff_key_from_event_with_no_staff_key(caplog):
    @redact_staff_key_from_event()
    def dummy_handler(event, context):
        return event

    # Arrange
    event = SQS_EVENT.copy()
    event["Records"][0]["body"] = dumps(PHARMACY_STANDARD_EVENT.copy())
    assert "Staff" not in extract_body(event["Records"][0]["body"])
    # Act
    result = dummy_handler(event, None)
    assert "Redacted 'Staff' key from Change Event payload" not in caplog.text
    assert "Staff" not in extract_body(result["Records"][0]["body"])


def test_redact_staff_key_from_event(caplog):
    @redact_staff_key_from_event()
    def dummy_handler(event, context):
        return event

    # Arrange
    event = SQS_EVENT.copy()
    event['Records'][0]['body'] = dumps(PHARMACY_STANDARD_EVENT_STAFF.copy())
    assert "Staff" in extract_body(event["Records"][0]["body"])
    # Act
    result = dummy_handler(event, None)
    assert "Redacted 'Staff' key from Change Event payload" in caplog.text
    assert "Staff" not in extract_body(result["Records"][0]["body"])


def test_unhandled_exception_logging(caplog):
    @unhandled_exception_logging
    def client_error_func(event, context):
        raise ClientError({"Error": {"Code": "dummy_error", "Message": "dummy_message"}}, "op_name")

    @unhandled_exception_logging
    def regular_error_func(event, context):
        raise Exception("dummy exception message")

    with caplog.at_level(logging.ERROR):

        with raises(ClientError):
            client_error_func(None, None)
        assert "Boto3 Client Error - 'dummy_error': dummy_message" in caplog.text

        with raises(Exception):
            regular_error_func(None, None)
        assert "dummy_error" in caplog.text


def test_unhandled_exception_logging_no_error():
    @unhandled_exception_logging
    def dummy_handler(event, context):
        pass

    # Arrange
    event = SQS_EVENT.copy()

    # Act
    dummy_handler(event, None)


def test_unhandled_exception_logging_hidden_event(caplog):
    @unhandled_exception_logging_hidden_event
    def regular_error_func(event, context):
        raise Exception("dummy exception message")

    with caplog.at_level(logging.ERROR):

        with raises(Exception):
            regular_error_func(None, None)
        assert "dummy_error" not in caplog.text


def test_unhandled_exception_logging_hidden_event_no_error():
    @unhandled_exception_logging_hidden_event
    def dummy_handler(event, context):
        pass

    # Arrange
    event = SQSEvent(None)
    # Act
    dummy_handler(event, None)


SQS_EVENT = {
    "Records": [
        {
            "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
            "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy0a...",
            "body": None,
            "attributes": {
                "ApproximateReceiveCount": "1",
                "SentTimestamp": "1642619743522",
                "SenderId": "AIDAIENQZJOLO23YVJ4VO",
                "ApproximateFirstReceiveTimestamp": "1545082649185",
            },
            "messageAttributes": {
                "correlation-id": {"stringValue": "1", "dataType": "String"},
                "sequence-number": {"stringValue": "1", "dataType": "Number"},
            },
            "md5OfBody": "e4e68fb7bd0e697a0ae8f1bb342846b3",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:my-queue",
            "awsRegion": "us-east-2",
        }
    ]
}
