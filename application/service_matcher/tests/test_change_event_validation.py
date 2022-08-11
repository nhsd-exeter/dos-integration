from unittest.mock import patch

import pytest
from pytest import raises

from ..change_event_validation import check_ods_code_length, validate_change_event, ValidationException

FILE_PATH = "application.service_matcher.change_event_validation"


@patch(f"{FILE_PATH}.validate_organisation_keys")
def test_validate_change_event(mock_validate_organisation_keys, change_event):
    # Act & Assert
    validate_change_event(change_event)


@patch(f"{FILE_PATH}.validate_organisation_keys")
@patch(f"{FILE_PATH}.check_ods_code_length")
def test_validate_change_event_missing_key(mock_check_ods_code_length, mock_validate_organisation_keys, change_event):
    # Arrange
    del change_event["ODSCode"]
    # Act
    with raises(ValidationException):
        validate_change_event(change_event)
    # Assert
    mock_check_ods_code_length.assert_not_called()
    mock_validate_organisation_keys.assert_not_called()


@pytest.mark.parametrize(
    "odscode, odscode_length",
    [
        ("FXXX1", 5),
        ("AAAAA", 5),
        ("00000", 5),
        ("V001234", 7),
    ],
)
def test_check_ods_code_length(odscode, odscode_length):
    # Act & Assert
    check_ods_code_length(odscode, odscode_length)


@pytest.mark.parametrize(
    "odscode, odscode_length",
    [
        ("FXXX11", 5),
        ("AAAA", 5),
        ("V0345", 7),
        ("V01234567", 7),
    ],
)
def test_check_ods_code_length_incorrect_length(odscode, odscode_length):
    # Act & Assert
    with raises(ValidationException):
        check_ods_code_length(odscode, odscode_length)
