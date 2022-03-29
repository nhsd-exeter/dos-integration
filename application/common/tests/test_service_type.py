import pytest
from pytest import raises
from common.change_event_exceptions import ValidationException

from ..constants import (
    DENTIST_SERVICE_KEY,
    ORGANISATION_SUB_TYPES_KEY,
    PHARMACY_SERVICE_KEY,
    SERVICE_TYPES,
    VALID_SERVICE_TYPES_KEY,
)
from ..service_type import ServiceType, get_valid_service_types

FILE_PATH = "application.common.test_service_type"


@pytest.mark.parametrize(
    "org_type, expected_service_type, expected_organisation_sub_type, expected_valid_service_types",
    [
        (
            "Dentist",
            DENTIST_SERVICE_KEY,
            SERVICE_TYPES["Dentist"][ORGANISATION_SUB_TYPES_KEY],
            SERVICE_TYPES["Dentist"][VALID_SERVICE_TYPES_KEY],
        ),
        (
            "PHA",
            PHARMACY_SERVICE_KEY,
            SERVICE_TYPES["PHA"][ORGANISATION_SUB_TYPES_KEY],
            SERVICE_TYPES["PHA"][VALID_SERVICE_TYPES_KEY],
        ),
    ],
)
def test_service_type(org_type, expected_service_type, expected_organisation_sub_type, expected_valid_service_types):
    # Act
    service_type = ServiceType(org_type)
    # Assert
    assert service_type.name == expected_service_type
    assert service_type.organisation_type_id == org_type
    assert service_type.organisation_sub_type == expected_organisation_sub_type
    assert service_type.valid_service_types == expected_valid_service_types


@pytest.mark.parametrize(
    "org_type",
    [("Pharmacy"), ("DEN")],
)
def test_service_type_exception(org_type):
    # Act & Assert
    with raises(ValidationException):
        ServiceType(org_type)


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
