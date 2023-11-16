from json import loads

import pytest
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord

from application.common.utilities import (
    extract_body,
    get_sequence_number,
    get_sqs_msg_attribute,
    handle_sqs_msg_attributes,
    is_val_none_or_empty,
    json_str_body,
)


def test_extract_body() -> None:
    # Arrange
    expected_change_event = '{"test": "test"}'
    # Act
    change_event = extract_body(expected_change_event)
    # Assert
    assert (
        loads(expected_change_event) == change_event
    ), f"Change event should be {loads(expected_change_event)} but is {change_event}"


def test_extract_body_exception() -> None:
    # Arrange
    expected_change_event = "test"
    # Act & Assert
    with pytest.raises(ValueError, match="Change Event unable to be extracted"):
        extract_body(expected_change_event)


def test_json_str_body() -> None:
    # Arrange
    expected_json_str = '{"test": "test"}'
    # Act
    result = json_str_body({"test": "test"})
    # Assert
    assert result == expected_json_str, f"Change event body should be {expected_json_str} str but is {result}"


def test_expected_json_str_exception() -> None:
    # Act & Assert
    with pytest.raises(TypeError, match="Object of type set is not JSON serializable"):
        json_str_body(body={"not a json dict"})


def test_get_sequence_number() -> None:
    # Arrange
    record = SQSRecord(SQS_EVENT["Records"][0])
    # Act
    sequence_number = get_sequence_number(record)
    # Assert
    assert sequence_number == int(SQS_EVENT["Records"][0]["messageAttributes"]["sequence-number"]["stringValue"])


def test_get_sequence_number_empty() -> None:
    # Arrange
    sqs_event = SQS_EVENT.copy()
    del sqs_event["Records"][0]["messageAttributes"]["sequence-number"]
    record = SQSRecord(sqs_event["Records"][0])
    # Act
    sequence_number = get_sequence_number(record)
    # Assert
    assert sequence_number is None


def test_get_sqs_msg_attribute_string(dead_letter_message: dict[str, str]) -> None:
    # Arrange
    attribute = "error_msg"
    msg_attributes = dead_letter_message["Records"][0]["messageAttributes"]
    # Act
    response = get_sqs_msg_attribute(msg_attributes=msg_attributes, key=attribute)
    # Assert
    assert response == msg_attributes[attribute]["stringValue"]


def test_get_sqs_msg_attribute_number(dead_letter_message: dict[str, str]) -> None:
    # Arrange
    attribute = "error_msg_http_code"
    msg_attributes = dead_letter_message["Records"][0]["messageAttributes"]
    # Act
    response = get_sqs_msg_attribute(msg_attributes=msg_attributes, key=attribute)
    # Assert
    assert response == float(msg_attributes[attribute]["stringValue"])


def test_get_sqs_msg_attribute_other(dead_letter_message: dict[str, str]) -> None:
    # Arrange
    attribute = "other"
    msg_attributes = dead_letter_message["Records"][0]["messageAttributes"]
    # Act
    response = get_sqs_msg_attribute(msg_attributes=msg_attributes, key=attribute)
    # Assert
    assert response is None


def test_get_sqs_msg_attribute_no_attributes() -> None:
    # Arrange
    msg_attributes = {}
    # Act
    response = get_sqs_msg_attribute(msg_attributes=msg_attributes, key="error_msg")
    # Assert
    assert response is None


def test_handle_sqs_msg_attributes(dead_letter_message: dict[str, str]) -> None:
    msg_attributes = dead_letter_message["Records"][0]["messageAttributes"]

    attributes = handle_sqs_msg_attributes(msg_attributes=msg_attributes)
    assert attributes["error_msg"] == msg_attributes["error_msg"]["stringValue"]
    assert attributes["error_msg_http_code"] == "400"


@pytest.mark.parametrize(("val", "expected"), [("", True), ("    ", True), (None, True), ("True val", False)])
def test_is_val_none_or_empty(val: str | None, expected: bool) -> None:
    assert is_val_none_or_empty(val) == expected


SQS_EVENT = {
    "Records": [
        {
            "messageId": "1",
            "receiptHandle": "3",
            "body": "Test message.",
            "attributes": {},
            "messageAttributes": {
                "sequence-number": {"stringValue": "1", "dataType": "Number"},
                "error_msg": {"stringValue": "Test Message", "dataType": "String"},
            },
            "md5OfBody": "e4e68fb7bd0e697a0ae8f1bb342846b3",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:my-queue",
            "awsRegion": "us-east-2",
        },
    ],
}
