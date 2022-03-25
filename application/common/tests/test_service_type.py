import pytest

from ..constants import (
    DENTIST_SERVICE_KEY,
    ORGANISATION_SUB_TYPES_KEY,
    PHARMACY_SERVICE_KEY,
    SERVICE_TYPES,
    VALID_SERVICE_TYPES_KEY,
)
from ..service_type import ServiceType

FILE_PATH = "application.common.test_service_type"


@pytest.mark.parametrize(
    "org_type, expected_service_type, expected_organisation_sub_type, expected_valid_service_types",
    [
        (
            "Dentist",
            DENTIST_SERVICE_KEY,
            SERVICE_TYPES[DENTIST_SERVICE_KEY][ORGANISATION_SUB_TYPES_KEY],
            SERVICE_TYPES[DENTIST_SERVICE_KEY][VALID_SERVICE_TYPES_KEY],
        ),
        (
            "PHA",
            PHARMACY_SERVICE_KEY,
            SERVICE_TYPES[PHARMACY_SERVICE_KEY][ORGANISATION_SUB_TYPES_KEY],
            SERVICE_TYPES[PHARMACY_SERVICE_KEY][VALID_SERVICE_TYPES_KEY],
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
