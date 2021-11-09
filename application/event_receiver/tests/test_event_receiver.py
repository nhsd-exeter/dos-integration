from json import loads
from os import environ
from unittest.mock import patch

import pytest
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from change_event_validation import ValidationException
from pytest import raises


from ..event_receiver import (
    FAILURE_STATUS_CODE,
    GENERIC_FAILURE_STATUS_RESPONSE,
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
@patch(f"{FILE_PATH}.valid_event")
def test_lambda_handler_valid_event(
    mock_valid_event, mock_trigger_event_processor, mock_set_return_value, mock_extract_event, change_event
):
    # Arrange
    context = LambdaContext()
    context._function_name = "test"
    context._aws_request_id = "test"
    mock_extract_event.return_value = change_event["body"]
    expected_return_value = {"statusCode": 100, "body": "example"}
    mock_set_return_value.return_value = expected_return_value
    mock_valid_event.return_value = True
    # Act
    response = lambda_handler(change_event, context)
    # Assert
    assert response == expected_return_value
    mock_extract_event.assert_called_once_with(change_event)
    mock_valid_event.assert_called_once_with(change_event["body"])
    mock_trigger_event_processor.assert_called_once_with(change_event["body"])
    mock_set_return_value.assert_called_once_with(SUCCESS_STATUS_CODE, SUCCESS_STATUS_RESPONSE)


@patch(f"{FILE_PATH}.extract_event")
@patch(f"{FILE_PATH}.set_return_value")
@patch(f"{FILE_PATH}.trigger_event_processor")
@patch(f"{FILE_PATH}.valid_event")
def test_lambda_handler_event_fails_validation(
    mock_valid_event, mock_trigger_event_processor, set_return_value, mock_extract_event, change_event
):
    # Arrange
    context = LambdaContext()
    context._function_name = "test"
    context._aws_request_id = "test"
    mock_extract_event.return_value = change_event["body"]
    expected_return_value = {"statusCode": 100, "body": "example"}
    set_return_value.return_value = expected_return_value
    mock_valid_event.return_value = False
    # Act
    response = lambda_handler(change_event, context)
    # Assert
    assert response == expected_return_value
    mock_extract_event.assert_called_once_with(change_event)
    mock_valid_event.assert_called_once_with(change_event["body"])
    mock_trigger_event_processor.assert_not_called()
    set_return_value.assert_called_once_with(FAILURE_STATUS_CODE, GENERIC_FAILURE_STATUS_RESPONSE)


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
    with raises(ValidationException) as exception:
        extract_event(event)
        assert exception.value.message == "Change Event incorrect format"
    log_capture.check(["lambda", "ERROR", "Change Event failed transformations"])


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
    environ["EVENT_PROCESSOR_NAME"] = event_processor_name
    change_event = change_event["body"]
    # Act
    trigger_event_processor(change_event)
    # Assert
    mock_invoke_lambda_function.assert_called_once_with(event_processor_name, change_event)
