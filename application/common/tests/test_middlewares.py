import logging
import re
from json import dumps

import pytest
from aws_lambda_powertools.utilities.data_classes import SQSEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from botocore.exceptions import ClientError

from application.common.middlewares import (
    redact_staff_key_from_event,
    unhandled_exception_logging,
    unhandled_exception_logging_hidden_event,
)
from application.common.utilities import extract_body
from application.conftest import PHARMACY_STANDARD_EVENT, PHARMACY_STANDARD_EVENT_STAFF


def test_redact_staff_key_from_event_with_no_staff_key(caplog: pytest.LogCaptureFixture):
    @redact_staff_key_from_event()
    def dummy_handler(event: dict[str, str], context: LambdaContext) -> SQSEvent:
        return event

    # Arrange
    event = SQS_EVENT.copy()
    event["Records"][0]["body"] = dumps(PHARMACY_STANDARD_EVENT.copy())
    assert "Staff" not in extract_body(event["Records"][0]["body"])
    # Act
    result = dummy_handler(event, None)
    assert "Checking if 'Staff' key needs removing from Change Event payload" in caplog.text
    assert "Redacted 'Staff' key from Change Event payload" not in caplog.text
    assert "Staff" not in extract_body(result["Records"][0]["body"])


def test_redact_staff_key_from_event(caplog: pytest.LogCaptureFixture):
    @redact_staff_key_from_event()
    def dummy_handler(event: dict[str, str], context: LambdaContext) -> SQSEvent:
        return event

    # Arrange
    event = SQS_EVENT.copy()
    event["Records"][0]["body"] = dumps(PHARMACY_STANDARD_EVENT_STAFF.copy())
    assert "Staff" in extract_body(event["Records"][0]["body"])
    # Act
    result = dummy_handler(event, None)
    assert "Checking if 'Staff' key needs removing from Change Event payload" in caplog.text
    assert "Redacted 'Staff' key from Change Event payload" in caplog.text
    assert "Staff" not in extract_body(result["Records"][0]["body"])


def test_redact_staff_key_from_event_no_records(caplog: pytest.LogCaptureFixture):
    @redact_staff_key_from_event()
    def dummy_handler(event: dict[str, str], context: LambdaContext) -> SQSEvent:
        return event

    # Arrange
    event = SQS_EVENT.copy()
    event["Records"] = []
    # Act
    result = dummy_handler(event, None)
    assert "Checking if 'Staff' key needs removing from Change Event payload" in caplog.text
    assert "Redacted 'Staff' key from Change Event payload" not in caplog.text
    assert len(result["Records"]) == 0


def test_unhandled_exception_logging(caplog: pytest.LogCaptureFixture):
    @unhandled_exception_logging
    def client_error_func(event: dict[str, str], context: LambdaContext) -> None:
        raise ClientError({"Error": {"Code": "dummy_error", "Message": "dummy_message"}}, "op_name")

    @unhandled_exception_logging
    def regular_error_func(event: dict[str, str], context: LambdaContext) -> None:
        msg = "dummy exception message"
        raise Exception(msg)  # noqa: TRY002

    with caplog.at_level(logging.ERROR):
        with pytest.raises(
            ClientError,
            match=re.escape("An error occurred (dummy_error) when calling the op_name operation: dummy_message"),
        ):
            client_error_func(None, None)

        with pytest.raises(Exception, match="dummy exception message"):
            regular_error_func(None, None)


def test_unhandled_exception_logging_no_error():
    @unhandled_exception_logging
    def dummy_handler(event: dict[str, str], context: LambdaContext) -> None:
        pass

    # Arrange
    event = SQS_EVENT.copy()

    # Act
    dummy_handler(event, None)


def test_unhandled_exception_logging_hidden_event(caplog: pytest.LogCaptureFixture):
    @unhandled_exception_logging_hidden_event
    def regular_error_func(event: dict[str, str], context: LambdaContext) -> None:
        msg = "dummy exception message"
        raise Exception(msg)  # noqa: TRY002

    with caplog.at_level(logging.ERROR):
        with pytest.raises(Exception, match="dummy exception message"):
            regular_error_func(None, None)
        assert "dummy_error" not in caplog.text


def test_unhandled_exception_logging_hidden_event_no_error():
    @unhandled_exception_logging_hidden_event
    def dummy_handler(event: dict[str, str], context: LambdaContext) -> None:
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
        },
    ],
}
