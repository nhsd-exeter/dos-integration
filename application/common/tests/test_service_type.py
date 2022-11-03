import pytest

from ..constants import SERVICE_TYPES, VALID_SERVICE_TYPES_KEY
from ..service_type import get_valid_service_types

FILE_PATH = "application.common.service_type"


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
