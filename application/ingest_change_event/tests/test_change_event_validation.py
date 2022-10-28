from unittest.mock import MagicMock, patch

import pytest
from pytest import raises

from ...ingest_change_event.change_event_validation import (
    check_ods_code_length,
    validate_change_event,
    validate_organisation_keys,
    validate_organisation_type_id,
    ValidationException,
)
from common.constants import DENTIST_ORG_TYPE_ID, PHARMACY_ORG_TYPE_ID

FILE_PATH = "application.ingest_change_event.change_event_validation"


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


@pytest.mark.parametrize(
    "org_type_id, org_sub_type",
    [
        (
            "Dentist",
            "TBA",
        ),
        (
            "PHA",
            "Community",
        ),
    ],
)
@patch(f"{FILE_PATH}.validate_organisation_type_id")
def test_validate_organisation_keys(
    mock_validate_organisation_type_id,
    org_type_id,
    org_sub_type,
):
    # Act & Assert
    validate_organisation_keys(org_type_id, org_sub_type)


@pytest.mark.parametrize(
    "org_type_id, org_sub_type",
    [
        (
            "Dentist",
            "RANDOM",
        ),
        (
            "PHA",
            "TEST1",
        ),
    ],
)
@patch(f"{FILE_PATH}.validate_organisation_type_id")
def test_validate_organisation_keys_org_sub_type_id_exception(
    mock_validate_organisation_type_id, org_type_id, org_sub_type
):
    # Act & Assert
    with raises(ValidationException) as exception:
        validate_organisation_keys(org_type_id, org_sub_type)
        assert f"Unexpected Org Sub Type ID: '{org_sub_type}'" in str(exception.value)


@pytest.mark.parametrize("org_type_id", [PHARMACY_ORG_TYPE_ID, DENTIST_ORG_TYPE_ID])
@patch(f"{FILE_PATH}.AppConfig")
def test_validate_organisation_type_id(mock_app_config, org_type_id):
    # Arrange
    feature_flags = MagicMock()
    mock_app_config().get_feature_flags.return_value = feature_flags
    feature_flags.evaluate.return_value = True
    # Act
    validate_organisation_type_id(org_type_id)
    # Assert
    feature_flags.evaluate.assert_called_once_with(
        name="accepted_org_types", context={"org_type": org_type_id}, default=False
    )


@pytest.mark.parametrize("org_type_id", [PHARMACY_ORG_TYPE_ID, DENTIST_ORG_TYPE_ID])
@patch(f"{FILE_PATH}.AppConfig")
def test_validate_organisation_type_id_wrong_org_type_id_exception(mock_app_config, org_type_id):
    # Arrange
    feature_flags = MagicMock()
    mock_app_config().get_feature_flags.return_value = feature_flags
    feature_flags.evaluate.return_value = False
    # Act
    with raises(ValidationException) as exception:
        validate_organisation_type_id(org_type_id)
        assert f"Unexpected Org Type ID: '{org_type_id}'" in str(exception.value)
    # Assert
    feature_flags.evaluate.assert_called_once_with(
        name="accepted_org_types", context={"org_type": org_type_id}, default=False
    )
    mock_app_config().get_raw_configuration.assert_called_once_with()
