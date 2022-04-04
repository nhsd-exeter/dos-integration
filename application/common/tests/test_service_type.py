import pytest
from pytest import raises
from common.change_event_exceptions import ValidationException

from ..constants import (
    SERVICE_TYPES,
    VALID_SERVICE_TYPES_KEY,
)
from ..service_type import get_valid_service_type_name, get_valid_service_types, validate_organisation_keys

FILE_PATH = "application.common.test_service_type"


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
def test_validate_organisation_keys(org_type_id, org_sub_type):
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
def test_validate_organisation_keys_org_sub_type_id_exception(org_type_id, org_sub_type):
    # Act & Assert
    with raises(ValidationException) as exception:
        validate_organisation_keys(org_type_id, org_sub_type)
        assert f"Unexpected Org Sub Type ID: '{org_sub_type}'" in str(exception.value)


@pytest.mark.parametrize(
    "org_type, expected_valid_service_types",
    [
        (
            "Dentist",
            SERVICE_TYPES["Dentist"][VALID_SERVICE_TYPES_KEY],
        ),
        (
            "PHA",
            SERVICE_TYPES["PHA"][VALID_SERVICE_TYPES_KEY],
        ),
    ],
)
def test_get_valid_service_types(org_type, expected_valid_service_types):
    # Act
    valid_service_types = get_valid_service_types(org_type)
    # Assert
    assert expected_valid_service_types == valid_service_types


@pytest.mark.parametrize(
    "org_type_id, expected_valid_service_name",
    [
        (
            "Dentist",
            "DENTIST",
        ),
        (
            "PHA",
            "PHARMACY",
        ),
        (
            "PHA1",
            None,
        ),
    ],
)
def test_get_valid_service_type_name(org_type_id, expected_valid_service_name):
    # Act
    valid_service_name = get_valid_service_type_name(org_type_id)
    # Assert
    assert expected_valid_service_name == valid_service_name
