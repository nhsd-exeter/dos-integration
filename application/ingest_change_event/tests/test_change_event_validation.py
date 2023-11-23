from unittest.mock import MagicMock, patch

import pytest

from application.ingest_change_event.change_event_validation import (
    ValidationError,
    check_ods_code_length,
    validate_change_event,
    validate_organisation_keys,
    validate_organisation_type_id,
)
from common.constants import PHARMACY_ORG_TYPE_ID

FILE_PATH = "application.ingest_change_event.change_event_validation"


@patch(f"{FILE_PATH}.validate_organisation_keys")
def test_validate_change_event(mock_validate_organisation_keys: MagicMock, change_event: dict[str, str]) -> None:
    # Act & Assert
    validate_change_event(change_event)


@patch(f"{FILE_PATH}.validate_organisation_keys")
@patch(f"{FILE_PATH}.check_ods_code_length")
def test_validate_change_event_missing_key(
    mock_check_ods_code_length: MagicMock, mock_validate_organisation_keys: MagicMock, change_event: dict[str, str]
) -> None:
    # Arrange
    del change_event["ODSCode"]
    # Act
    with pytest.raises(ValidationError):
        validate_change_event(change_event)
    # Assert
    mock_check_ods_code_length.assert_not_called()
    mock_validate_organisation_keys.assert_not_called()


@pytest.mark.parametrize(
    ("odscode"),
    [
        ("FXXX1"),
        ("AAAAA"),
        ("00000"),
    ],
)
def test_check_ods_code_length(odscode: str) -> None:
    # Act & Assert
    check_ods_code_length(odscode)


@pytest.mark.parametrize(
    ("odscode"),
    [
        ("FXXX11"),
        ("AAAA"),
        ("V0345A"),
        ("V01234567"),
    ],
)
def test_check_ods_code_length_incorrect_length(odscode: str) -> None:
    # Act & Assert
    with pytest.raises(ValidationError):
        check_ods_code_length(odscode)


@pytest.mark.parametrize(
    ("org_type_id", "org_sub_type"),
    [
        (
            "PHA",
            "Community",
        ),
    ],
)
@patch(f"{FILE_PATH}.validate_organisation_type_id")
def test_validate_organisation_keys(
    mock_validate_organisation_type_id: MagicMock,
    org_type_id: str,
    org_sub_type: str,
) -> None:
    # Act & Assert
    validate_organisation_keys(org_type_id, org_sub_type)


@pytest.mark.parametrize(
    ("org_type_id", "org_sub_type"),
    [
        (
            "GP",
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
    mock_validate_organisation_type_id: MagicMock,
    org_type_id: str,
    org_sub_type: str,
) -> None:
    # Act & Assert
    with pytest.raises(ValidationError) as exception:
        validate_organisation_keys(org_type_id, org_sub_type)
    assert f"Unexpected Org Sub Type ID: '{org_sub_type}'" in str(exception.value)


@pytest.mark.parametrize("org_type_id", [PHARMACY_ORG_TYPE_ID])
def test_validate_organisation_type_id(org_type_id: str) -> None:
    # Act
    response = validate_organisation_type_id(org_type_id)
    # Assert
    assert response is None


@pytest.mark.parametrize("org_type_id", ["GP", "DEN", "TEST1"])
def test_validate_organisation_type_id_wrong_org_type_id_exception(org_type_id: str) -> None:
    # Act & Assert
    with pytest.raises(ValidationError) as exception:
        validate_organisation_type_id(org_type_id)
    assert f"Unexpected Org Type ID: '{org_type_id}'" in str(exception.value)
