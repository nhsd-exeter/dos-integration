from unittest.mock import patch

import pytest
from pytest import fixture, raises
from testfixtures import LogCapture

from ..change_event_validation import (
    ValidationException,
    check_ods_code_length,
    check_service_sub_type,
    check_service_type,
    valid_event,
)
from .change_event import PHARMACY_STANDARD_EVENT

FILE_PATH = "application.event_receiver.change_event_validation"


def test_valid_event(change_event):
    # Act
    response = valid_event(change_event["body"])
    # Assert
    assert response is True


@patch(f"{FILE_PATH}.check_service_sub_type")
@patch(f"{FILE_PATH}.check_service_type")
@patch(f"{FILE_PATH}.check_ods_code_length")
def test_validate_event_missing_key(
    mock_check_ods_code_length, mock_check_service_type, mock_check_service_sub_type, change_event, log_capture
):
    # Arrange
    del change_event["body"]["ODSCode"]
    # Act
    response = valid_event(change_event["body"])
    # Assert
    mock_check_ods_code_length.assert_not_called()
    mock_check_service_type.assert_not_called()
    mock_check_service_sub_type.assert_not_called()
    assert "Input schema validation error|" in log_capture[0][2]
    assert response is False


@pytest.mark.parametrize("service_type", ["PHA"])
def test_check_service_type(service_type):
    # Act & Assert
    check_service_type(service_type)


@pytest.mark.parametrize("service_type", ["Not Expected Type", "Dentist", "Pharmacy Out of hours", "PH1"])
def test_check_service_type_wrong_service_type(service_type):
    # Act & Assert
    with raises(ValidationException):
        check_service_type(service_type)


@pytest.mark.parametrize("service_sub_type", ["COMPH"])
def test_check_service_sub_type(service_sub_type):
    # Act & Assert
    check_service_sub_type(service_sub_type)


@pytest.mark.parametrize("service_sub_type", ["Pharmacy", "PH1"])
def test_check_service_sub_type_wrong_service_sub_type(service_sub_type):
    # Act & Assert
    with raises(ValidationException):
        check_service_sub_type(service_sub_type)


@pytest.mark.parametrize("odscode", ["FXXX1", "AAAAA", "00000"])
def test_check_ods_code_length(odscode):
    # Act & Assert
    check_ods_code_length(odscode)


@pytest.mark.parametrize("odscode", ["FXXX11", "AAAA"])
def test_check_ods_code_length_incorrect_length(odscode):
    # Act & Assert
    with raises(ValidationException):
        check_ods_code_length(odscode)


@fixture()
def log_capture():
    with LogCapture(names="lambda") as capture:
        yield capture


@fixture
def change_event():
    change_event = PHARMACY_STANDARD_EVENT.copy()
    yield change_event
