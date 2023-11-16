from unittest.mock import MagicMock, patch

from application.conftest import dummy_dos_service
from application.service_matcher.matching import get_matching_services
from common.nhs import NHSEntity

FILE_PATH = "application.service_matcher.matching"


@patch(f"{FILE_PATH}.get_matching_dos_services")
def test_get_matching_services(mock_get_matching_dos_services: MagicMock, change_event):
    # Arrange
    nhs_entity = NHSEntity(change_event)
    service = dummy_dos_service()
    service.typeid = 13
    service.statusid = 1
    mock_get_matching_dos_services.return_value = [service]
    # Act
    matching_services = get_matching_services(nhs_entity)
    # Assert
    assert matching_services == [service]


@patch(f"{FILE_PATH}.get_matching_dos_services")
def test_get_unmatching_services(mock_get_matching_dos_services: MagicMock, change_event):
    # Arrange
    nhs_entity = NHSEntity(change_event)
    mock_get_matching_dos_services.return_value = []
    # Act
    response = get_matching_services(nhs_entity)
    # Assert
    assert response == []
