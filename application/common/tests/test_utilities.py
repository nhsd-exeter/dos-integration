from json import loads

from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord

from pytest import raises, mark
from ..utilities import (
    extract_body,
    get_sequence_number,
    get_sqs_msg_attribute,
    handle_sqs_msg_attributes,
    is_val_none_or_empty,
    remove_given_keys_from_dict_by_msg_limit,
)


def test_extract_body():
    # Arrange
    expected_change_event = '{"test": "test"}'
    # Act
    change_event = extract_body(expected_change_event)
    # Assert
    assert (
        loads(expected_change_event) == change_event
    ), f"Change event should be {loads(expected_change_event)} but is {change_event}"


def test_extract_body_exception():
    # Arrange
    expected_change_event = {"test": "test"}
    # Act & Assert
    with raises(Exception):
        extract_body(expected_change_event)


def test_get_sequence_number():
    # Arrange
    record = SQSRecord(SQS_EVENT["Records"][0])
    # Act
    sequence_number = get_sequence_number(record)
    # Assert
    assert sequence_number == int(SQS_EVENT["Records"][0]["messageAttributes"]["sequence-number"]["stringValue"])


def test_get_sequence_number_empty():
    # Arrange
    sqs_event = SQS_EVENT.copy()
    del sqs_event["Records"][0]["messageAttributes"]["sequence-number"]
    record = SQSRecord(sqs_event["Records"][0])
    # Act
    sequence_number = get_sequence_number(record)
    # Assert
    assert sequence_number is None


def test_get_sqs_msg_attribute_string(dead_letter_message):
    # Arrange
    attribute = "error_msg"
    msg_attributes = dead_letter_message["Records"][0]["messageAttributes"]
    # Act
    response = get_sqs_msg_attribute(msg_attributes=msg_attributes, key=attribute)
    # Assert
    assert response == msg_attributes[attribute]["stringValue"]


def test_get_sqs_msg_attribute_number(dead_letter_message):
    # Arrange
    attribute = "error_msg_http_code"
    msg_attributes = dead_letter_message["Records"][0]["messageAttributes"]
    # Act
    response = get_sqs_msg_attribute(msg_attributes=msg_attributes, key=attribute)
    # Assert
    assert response == float(msg_attributes[attribute]["stringValue"])


def test_get_sqs_msg_attribute_other(dead_letter_message):
    # Arrange
    attribute = "other"
    msg_attributes = dead_letter_message["Records"][0]["messageAttributes"]
    # Act
    response = get_sqs_msg_attribute(msg_attributes=msg_attributes, key=attribute)
    # Assert
    assert response is None


def test_get_sqs_msg_attribute_no_attributes():
    # Arrange
    msg_attributes = {}
    # Act
    response = get_sqs_msg_attribute(msg_attributes=msg_attributes, key="error_msg")
    # Assert
    assert response is None


def test_handle_sqs_msg_attributes(dead_letter_message):
    msg_attributes = dead_letter_message["Records"][0]["messageAttributes"]

    attributes = handle_sqs_msg_attributes(msg_attributes=msg_attributes)
    assert attributes["error_msg"] == msg_attributes["error_msg"]["stringValue"]
    assert attributes["error_msg_http_code"] == "400"


@mark.parametrize("val,expected", [("", True), ("    ", True), (None, True), ("True val", False)])
def test_is_val_none_or_empty(val, expected):
    assert is_val_none_or_empty(val) == expected


@mark.parametrize("input_dict,keys_tobe_removed,msg_limit,expected", [
    ({"Name": "John", "Address": ["2", "4"], "Age": 34}, ["Address"], 20, {"Name": "John", "Age": 34}),
    ({"Name": "John", "Address": ["2", "4"], "Age": 34}, ["Address", "Age"], 20, {"Name": "John"}),
    ({"Name": "John", "Address": ["2", "4"], "Age": 34}, [""], 20, {"Name": "John", "Address": ["2", "4"], "Age": 34}),
    ({"Name": "John", "Age": 34}, ["Age"], 120, {"Name": "John", "Age": 34})
    ])
def test_remove_given_keys_from_dict_by_msg_limit(input_dict, keys_tobe_removed, msg_limit, expected):
    event = remove_given_keys_from_dict_by_msg_limit(input_dict, keys_tobe_removed, msg_limit)
    assert (
        event == expected
    ), f"Change event should be {expected} but is {event}"


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
        }
    ]
}
