from unittest.mock import patch

import pytest
from common.service_type import ServiceType
from pytest import raises

from ..change_event_validation import ValidationException, check_ods_code_length, validate_event

FILE_PATH = "application.event_processor.change_event_validation"


def test_validate_event(change_event):
    # Act & Assert
    validate_event(change_event)


@patch(f"{FILE_PATH}.validate_organisation_keys")
@patch(f"{FILE_PATH}.check_ods_code_length")
def test_validate_event_missing_key(mock_check_ods_code_length, mock_validate_organisation_keys, change_event):
    # Arrange
    del change_event["ODSCode"]
    # Act
    with raises(ValidationException):
        validate_event(change_event)
    # Assert
    mock_check_ods_code_length.assert_not_called()
    mock_validate_organisation_keys.assert_not_called()


@pytest.mark.parametrize("odscode", ["FXXX1", "AAAAA", "00000"])
def test_check_ods_code_length(odscode):
    # Act & Assert
    check_ods_code_length(odscode)


@pytest.mark.parametrize("odscode", ["FXXX11", "AAAA"])
def test_check_ods_code_length_incorrect_length(odscode):
    # Act & Assert
    with raises(ValidationException):
        check_ods_code_length(odscode)
