from os import environ
from unittest.mock import patch

import pytest
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext

from ..event_receiver import get_return_value, lambda_handler, trigger_event_processor
from .change_events import PHARMACY_STANDARD_EVENT

FILE_PATH = "application.event_receiver.event_receiver"


@patch(f"{FILE_PATH}.get_return_value")
@patch(f"{FILE_PATH}.trigger_event_processor")
@patch(f"{FILE_PATH}.validate_event")
def test_lambda_handler_valid_event(mock_validate_event, mock_trigger_event_processor, mock_get_return_value):
    # Arrange
    context = LambdaContext()
    context._function_name = "test"
    context._aws_request_id = "test"
    mock_validate_event.return_value = True
    expected_return_value = {"statusCode": 100, "body": "example"}
    mock_get_return_value.return_value = expected_return_value
    # Act
    response = lambda_handler(PHARMACY_STANDARD_EVENT, context)
    # Assert
    mock_trigger_event_processor.assert_called_once_with()
    mock_get_return_value.assert_called_once_with(200, "Change Event Accepted")
    assert response == expected_return_value


@patch(f"{FILE_PATH}.get_return_value")
@patch(f"{FILE_PATH}.trigger_event_processor")
@patch(f"{FILE_PATH}.validate_event")
def test_lambda_handler_invalid_event(mock_validate_event, mock_trigger_event_processor, mock_get_return_value):
    # Arrange
    context = LambdaContext()
    context._function_name = "test"
    context._aws_request_id = "test"
    mock_validate_event.return_value = False
    expected_return_value = {"statusCode": 100, "body": "example"}
    mock_get_return_value.return_value = expected_return_value
    # Act
    response = lambda_handler(PHARMACY_STANDARD_EVENT, context)
    # Assert
    mock_trigger_event_processor.assert_not_called()
    mock_get_return_value.assert_called_once_with(400, "Bad Change Event Received")
    assert response == expected_return_value


def test_get_return_value():
    # Arrange
    status_code = 200
    message = "example"
    # Act
    response = get_return_value(status_code, message)
    # Assert
    assert response == {"statusCode": status_code, "body": '{"body": "' + message + '"}'}


@pytest.mark.parametrize("is_mock_mode_value", [True])
@patch(f"{FILE_PATH}.invoke_lambda_function")
@patch(f"{FILE_PATH}.is_mock_mode")
def test_trigger_event_processor_mock_mode(mock_is_mock_mode, mock_invoke_lambda_function, is_mock_mode_value):
    # Arrange
    mock_is_mock_mode.return_value = is_mock_mode_value
    # Act
    trigger_event_processor()
    # Assert
    mock_invoke_lambda_function.assert_not_called()


@pytest.mark.parametrize("is_mock_mode_value", [False, "any", None, "", 1])
@patch(f"{FILE_PATH}.invoke_lambda_function")
@patch(f"{FILE_PATH}.is_mock_mode")
def test_trigger_event_processor_not_mock_mode(mock_is_mock_mode, mock_invoke_lambda_function, is_mock_mode_value):
    # Arrange
    mock_is_mock_mode.return_value = is_mock_mode_value
    event_processor_name = "event_processor"
    environ["EVENT_PROCESSOR_NAME"] = event_processor_name
    # Act
    trigger_event_processor()
    # Assert
    mock_invoke_lambda_function.assert_called_once_with(event_processor_name)
