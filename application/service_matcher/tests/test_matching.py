from os import environ
from unittest.mock import MagicMock, patch

from application.conftest import dummy_dos_service
from application.service_matcher.matching import get_matching_services, get_pharmacy_first_phase_one_feature_flag
from common.nhs import NHSEntity

FILE_PATH = "application.service_matcher.matching"


@patch(f"{FILE_PATH}.get_pharmacy_first_phase_one_feature_flag")
@patch(f"{FILE_PATH}.get_matching_dos_services")
def test_get_matching_services(
    mock_get_matching_dos_services: MagicMock,
    mock_get_pharmacy_first_phase_one_feature_flag: MagicMock,
    change_event: dict[str, str],
):
    # Arrange
    nhs_entity = NHSEntity(change_event)
    service = dummy_dos_service()
    service.typeid = 13
    service.statusid = 1
    mock_get_matching_dos_services.return_value = [service]
    mock_get_pharmacy_first_phase_one_feature_flag.return_value = True
    # Act
    matching_services = get_matching_services(nhs_entity)
    # Assert
    assert matching_services == [service]
    mock_get_pharmacy_first_phase_one_feature_flag.assert_called_once()


@patch(f"{FILE_PATH}.get_pharmacy_first_phase_one_feature_flag")
@patch(f"{FILE_PATH}.get_matching_dos_services")
def test_get_unmatching_services(
    mock_get_matching_dos_services: MagicMock,
    mock_get_pharmacy_first_phase_one_feature_flag: MagicMock,
    change_event: dict[str, str],
):
    # Arrange
    nhs_entity = NHSEntity(change_event)
    mock_get_matching_dos_services.return_value = []
    mock_get_pharmacy_first_phase_one_feature_flag.return_value = True
    # Act
    response = get_matching_services(nhs_entity)
    # Assert
    assert response == []
    mock_get_pharmacy_first_phase_one_feature_flag.assert_called_once()


@patch(f"{FILE_PATH}.parameters.get_parameter")
def test_get_pharmacy_first_phase_one_feature_flag(mock_get_parameter: MagicMock) -> None:
    # Arrange
    environ["PHARMACY_FIRST_PHASE_ONE_PARAMETER"] = environment_variable = "test"
    mock_get_parameter.return_value = "True"
    # Act
    response = get_pharmacy_first_phase_one_feature_flag()
    # Assert
    assert response is True
    mock_get_parameter.assert_called_once_with(environment_variable)
    # Clean up
    del environ["PHARMACY_FIRST_PHASE_ONE_PARAMETER"]
