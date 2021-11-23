from json import loads
from os import environ
from unittest.mock import patch

import pytest
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from change_event_validation import ValidationException
from pytest import raises


from ..event_receiver import (
    FAILURE_STATUS_CODE,
    UNEXPECTED_SERVER_ERROR_STATUS_CODE,
    UNEXPECTED_SERVER_ERROR_RESPONSE,
    SUCCESS_STATUS_CODE,
    SUCCESS_STATUS_RESPONSE,
    extract_event,
    lambda_handler,
    trigger_event_processor,
)

FILE_PATH = "application.event_receiver.event_receiver"


@patch(f"{FILE_PATH}.extract_event")
@patch(f"{FILE_PATH}.set_return_value")
@patch(f"{FILE_PATH}.trigger_event_processor")
@patch(f"{FILE_PATH}.validate_event")
def test_lambda_handler_valid_event(
    mock_validate_event, mock_trigger_event_processor, mock_set_return_value, mock_extract_event, change_event
):
    # Arrange
    context = LambdaContext()
    context._function_name = "test"
    context._aws_request_id = "test"
    mock_extract_event.return_value = change_event["body"]
    expected_return_value = {"statusCode": 100, "body": "example"}
    mock_set_return_value.return_value = expected_return_value
    # Act
    lambda_handler(change_event, context)
    # Assert
    mock_extract_event.assert_called_once_with(change_event)
    mock_validate_event.assert_called_once_with(change_event["body"])
    mock_trigger_event_processor.assert_called_once_with(change_event["body"])
    mock_set_return_value.assert_called_once_with(SUCCESS_STATUS_CODE, SUCCESS_STATUS_RESPONSE)


@patch(f"{FILE_PATH}.extract_event")
@patch(f"{FILE_PATH}.set_return_value")
@patch(f"{FILE_PATH}.trigger_event_processor")
@patch(f"{FILE_PATH}.validate_event")
def test_lambda_handler_event_fails_validation(
    mock_validate_event, mock_trigger_event_processor, set_return_value, mock_extract_event, change_event
):
    # Arrange
    context = LambdaContext()
    context._function_name = "test"
    context._aws_request_id = "test"
    mock_extract_event.return_value = change_event["body"]
    expected_return_value = {"statusCode": 100, "body": "example"}
    set_return_value.return_value = expected_return_value
    error_message = "Invalid event"
    mock_validate_event.side_effect = ValidationException(error_message)
    # Act
    lambda_handler(change_event, context)
    # Assert
    mock_extract_event.assert_called_once_with(change_event)
    mock_validate_event.assert_called_once_with(change_event["body"])
    mock_trigger_event_processor.assert_not_called()
    set_return_value.assert_called_once_with(FAILURE_STATUS_CODE, error_message)


@patch(f"{FILE_PATH}.extract_event")
@patch(f"{FILE_PATH}.set_return_value")
@patch(f"{FILE_PATH}.trigger_event_processor")
@patch(f"{FILE_PATH}.validate_event")
def test_lambda_handler_event_unexpected_failure(
    mock_validate_event, mock_trigger_event_processor, set_return_value, mock_extract_event, change_event
):
    # Arrange
    context = LambdaContext()
    context._function_name = "test"
    context._aws_request_id = "test"
    mock_extract_event.return_value = change_event["body"]
    expected_return_value = {"statusCode": 100, "body": "example"}
    set_return_value.return_value = expected_return_value
    mock_validate_event.side_effect = KeyError("Test")
    # Act
    lambda_handler(change_event, context)
    # Assert
    mock_extract_event.assert_called_once_with(change_event)
    mock_validate_event.assert_called_once_with(change_event["body"])
    mock_trigger_event_processor.assert_not_called()
    set_return_value.assert_called_once_with(UNEXPECTED_SERVER_ERROR_STATUS_CODE, UNEXPECTED_SERVER_ERROR_RESPONSE)


def test_extract_event():
    # Arrange
    event = {"body": '{"example" : "Test"}'}
    # Act
    response = extract_event(event)
    # Assert
    assert loads(event["body"]) == response


def test_extract_event_invalid_event(log_capture):
    # Arrange
    event = {"other": "example"}
    # Act & Assert
    with raises(KeyError):
        extract_event(event)
    log_capture.check(["lambda", "ERROR", "Change Event unable to be extracted"])


@pytest.mark.parametrize("is_mock_mode_value", [True])
@patch(f"{FILE_PATH}.invoke_lambda_function")
@patch(f"{FILE_PATH}.is_mock_mode")
def test_trigger_event_processor_mock_mode(
    mock_is_mock_mode, mock_invoke_lambda_function, is_mock_mode_value, change_event
):
    # Arrange
    mock_is_mock_mode.return_value = is_mock_mode_value
    change_event = change_event["body"]
    # Act
    trigger_event_processor(change_event)
    # Assert
    mock_invoke_lambda_function.assert_not_called()


@pytest.mark.parametrize("is_mock_mode_value", [False, "any", None, "", 1])
@patch(f"{FILE_PATH}.invoke_lambda_function")
@patch(f"{FILE_PATH}.is_mock_mode")
def test_trigger_event_processor_not_mock_mode(
    mock_is_mock_mode, mock_invoke_lambda_function, is_mock_mode_value, change_event
):
    # Arrange
    mock_is_mock_mode.return_value = is_mock_mode_value
    event_processor_name = "event_processor"
    environ["EVENT_PROCESSOR_LAMBDA_NAME"] = event_processor_name
    change_event = change_event["body"]
    # Act
    trigger_event_processor(change_event)
    # Assert
    mock_invoke_lambda_function.assert_called_once_with(event_processor_name, change_event)
