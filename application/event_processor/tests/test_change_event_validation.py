from unittest.mock import patch

import pytest
from pytest import raises

from ..change_event_validation import (
    ValidationException,
    check_ods_code_length,
    check_org_type_id,
    check_org_sub_type,
    validate_event,
)


FILE_PATH = "application.event_processor.change_event_validation"


def test_validate_event(change_event):
    # Act & Assert
    validate_event(change_event)


@patch(f"{FILE_PATH}.check_org_sub_type")
@patch(f"{FILE_PATH}.check_org_type_id")
@patch(f"{FILE_PATH}.check_ods_code_length")
def test_validate_event_missing_key(
    mock_check_ods_code_length, mock_check_org_type_id, mock_check_org_sub_type, change_event, log_capture
):
    # Arrange
    del change_event["ODSCode"]
    # Act
    with raises(ValidationException):
        validate_event(change_event)
    # Assert
    mock_check_ods_code_length.assert_not_called()
    mock_check_org_type_id.assert_not_called()
    mock_check_org_sub_type.assert_not_called()


@pytest.mark.parametrize("org_type", ["PHA"])
def test_check_org_type_id(org_type):
    # Act & Assert
    check_org_type_id(org_type)


@pytest.mark.parametrize("org_type", ["Not Expected Type", "Dentist", "Pharmacy Out of hours", "PH1"])
def test_check_org_type_id_wrong_org_type(org_type):
    # Act & Assert
    with raises(ValidationException):
        check_org_type_id(org_type)


@pytest.mark.parametrize("org_sub_type", ["Community"])
def test_check_org_sub_type(org_sub_type):
    # Act & Assert
    check_org_sub_type(org_sub_type)


@pytest.mark.parametrize("org_sub_type", ["Pharmacy", "PH1"])
def test_check_org_sub_type_wrong_org_sub_type(org_sub_type):
    # Act & Assert
    with raises(ValidationException):
        check_org_sub_type(org_sub_type)


@pytest.mark.parametrize("odscode", ["FXXX1", "AAAAA", "00000"])
def test_check_ods_code_length(odscode):
    # Act & Assert
    check_ods_code_length(odscode)


@pytest.mark.parametrize("odscode", ["FXXX11", "AAAA"])
def test_check_ods_code_length_incorrect_length(odscode):
    # Act & Assert
    with raises(ValidationException):
        check_ods_code_length(odscode)
