from unittest.mock import patch

import pytest

from ..event_validation import check_ods_code_type_and_length, check_organisation_type, validate_event, INPUT_SCHEMA
from .change_events import PHARMACY_STANDARD_EVENT

FILE_PATH = "application.event_receiver.event_validation"


def test_validate_event():
    # Act
    response = validate_event(PHARMACY_STANDARD_EVENT["body"])
    # Assert
    assert response is True


@patch(f"{FILE_PATH}.validate")
@patch(f"{FILE_PATH}.check_organisation_type")
@patch(f"{FILE_PATH}.check_ods_code_type_and_length")
def test_validate_event_organisation_type_invalid(
    mock_check_ods_code_type_and_length, mock_check_organisation_type, mock_validate
):
    # Arrange
    event = PHARMACY_STANDARD_EVENT.copy()
    change_event = event["body"]
    organisation_type = change_event["OrganisationType"]
    mock_check_organisation_type.return_value = False
    # Act
    response = validate_event(change_event)
    # Assert
    mock_validate.assert_called_once_with(event=change_event, schema=INPUT_SCHEMA)
    mock_check_organisation_type.assert_called_with(organisation_type=organisation_type)
    mock_check_ods_code_type_and_length.assert_not_called()
    assert response is False


@patch(f"{FILE_PATH}.validate")
@patch(f"{FILE_PATH}.check_organisation_type")
@patch(f"{FILE_PATH}.check_ods_code_type_and_length")
def test_validate_event_odscode_invalid(
    mock_check_ods_code_type_and_length, mock_check_organisation_type, mock_validate
):
    # Arrange
    event = PHARMACY_STANDARD_EVENT.copy()
    change_event = event["body"]
    organisation_type = change_event["OrganisationType"]
    odscode = change_event["ODSCode"]
    mock_check_organisation_type.return_value = True
    mock_check_ods_code_type_and_length.return_value = False
    # Act
    response = validate_event(change_event)
    # Assert
    mock_validate.assert_called_once_with(event=change_event, schema=INPUT_SCHEMA)
    mock_check_organisation_type.assert_called_with(organisation_type=organisation_type)
    mock_check_ods_code_type_and_length.assert_called_with(odscode=odscode)
    assert response is False


@patch(f"{FILE_PATH}.check_organisation_type")
@patch(f"{FILE_PATH}.check_ods_code_type_and_length")
def test_validate_event_missing_key(mock_check_ods_code_type_and_length, mock_check_organisation_type):
    # Arrange
    event = PHARMACY_STANDARD_EVENT.copy()
    del event["body"]["ODSCode"]
    # Act
    response = validate_event(event)
    # Assert
    mock_check_ods_code_type_and_length.assert_not_called()
    mock_check_organisation_type.assert_not_called()
    assert response is False


@patch(f"{FILE_PATH}.check_organisation_type")
def test_validate_event_incorrect_organisation_type(mock_check_organisation_type):
    # Arrange
    mock_check_organisation_type.return_value = False
    # Act
    response = validate_event(PHARMACY_STANDARD_EVENT)
    # Assert
    response is False


@patch(f"{FILE_PATH}.check_ods_code_type_and_length")
def test_validate_event_incorrect_odscode(mock_check_ods_code_type_and_length):
    # Arrange
    mock_check_ods_code_type_and_length.return_value = False
    # Act
    response = validate_event(PHARMACY_STANDARD_EVENT)
    # Assert
    response is False


@pytest.mark.parametrize("organisation_type", ["Pharmacy"])
def test_check_organisation_type(organisation_type):
    # Act
    response = check_organisation_type(organisation_type)
    # Assert
    assert response is True


@pytest.mark.parametrize("organisation_type", ["Not Expected Type", "Dentist", "Pharmacy Out of hours"])
def test_check_organisation_type_wrong_organisation_type(organisation_type):
    # Act
    response = check_organisation_type(organisation_type)
    # Assert
    assert response is False


@pytest.mark.parametrize("odscode", ["FXXX1", "AAAAA", "00000"])
def test_check_ods_code_type_and_length(odscode):
    # Act
    response = check_ods_code_type_and_length(odscode)
    # Assert
    assert response is True


@pytest.mark.parametrize("odscode", ["FXXX11", "AAAA"])
def test_check_ods_code_type_and_length_incorrect_length(odscode):
    # Act
    response = check_ods_code_type_and_length(odscode)
    # Assert
    assert response is False


@pytest.mark.parametrize("odscode", [["Pharmacy"], 00000])
def test_check_ods_code_type_and_length_incorrect_format(odscode):
    # Act
    response = check_ods_code_type_and_length(odscode)
    # Assert
    assert response is False
