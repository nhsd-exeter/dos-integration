from json import dumps, loads
from os import environ
from unittest.mock import patch
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord

from pytest import raises

from ..utilities import (
    extract_body,
    get_environment_variable,
    invoke_lambda_function,
    is_debug_mode,
    is_mock_mode,
    get_sequence_number,
)

FILE_PATH = "application.common.utilities"


def test_is_debug_mode_true_local():
    # Arrange
    environ["PROFILE"] = "local"
    # Act
    result = is_debug_mode()
    # Assert
    assert result is True
    # Clean up
    del environ["PROFILE"]


def test_is_debug_mode_true_task():
    # Arrange
    environ["PROFILE"] = "task"
    # Act
    result = is_debug_mode()
    # Assert
    assert result is True
    # Clean up
    del environ["PROFILE"]


def test_is_debug_mode_false():
    # Arrange
    environ["PROFILE"] = "remote"
    # Act
    result = is_debug_mode()
    # Assert
    assert result is False
    # Clean up
    del environ["PROFILE"]


def test_is_get_environment_variable():
    # Arrange
    other_variable_key = "OTHER_VAR"
    other_variable_value = "my-var"
    environ[other_variable_key] = other_variable_value
    # Act
    env_var = get_environment_variable(other_variable_key)
    # Assert
    assert env_var == other_variable_value
    # Clean up
    del environ[other_variable_key]


def test_get_environment_variable_key_error():
    # Act & Assert
    with raises(KeyError):
        get_environment_variable("UNKNOWN_VARIABLE")


def test_is_mock_mode():
    # Arrange
    mock_mode = True
    environ["MOCK_MODE"] = str(mock_mode)
    # Act
    response = is_mock_mode()
    # Assert
    assert response == mock_mode
    # Clean up
    del environ["MOCK_MODE"]


def test_is_mock_mode_none():
    # Arrange
    expected_response = False
    # Act
    response = is_mock_mode()
    # Assert
    assert response == expected_response


@patch(f"{FILE_PATH}.client")
def test_invoke_lambda_function(mock_client):
    # Arrange
    lambda_function_name = "my-lambda-function"
    payload = {"test": "test"}
    # Act
    invoke_lambda_function(lambda_function_name, payload)
    # Assert
    mock_client.assert_called_once_with("lambda")
    mock_client.return_value.invoke.assert_called_once_with(
        FunctionName=lambda_function_name, InvocationType="Event", Payload=dumps(payload).encode("utf-8")
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


SQS_EVENT = {
    "Records": [
        {
            "messageId": "1",
            "receiptHandle": "3",
            "body": "Test message.",
            "attributes": {},
            "messageAttributes": {
                "sequence-number": {"stringValue": "1", "dataType": "Number"},
            },
            "md5OfBody": "e4e68fb7bd0e697a0ae8f1bb342846b3",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:my-queue",
            "awsRegion": "us-east-2",
        }
    ]
}
