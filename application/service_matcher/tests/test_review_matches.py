from unittest.mock import MagicMock, patch

from .test_service_matcher import PHARMACY_STANDARD_EVENT
from application.common.nhs import NHSEntity
from application.conftest import dummy_dos_service
from application.service_matcher.review_matches import (
    check_for_missing_dos_services,
    check_for_missing_palliative_care_service,
    remove_service_if_not_on_change_event,
    review_matches,
)
from common.commissioned_service_type import BLOOD_PRESSURE, PALLIATIVE_CARE

FILE_PATH = "application.service_matcher.review_matches"


def test_review_changes() -> None:
    # Arrange
    service = dummy_dos_service()
    service.typeid = 13
    service.statusid = 1
    matching_services = [service]
    nhs_entity = NHSEntity(PHARMACY_STANDARD_EVENT)
    # Act
    response = review_matches(matching_services, nhs_entity)
    # Assert
    assert response == matching_services


@patch(f"{FILE_PATH}.log_closed_or_hidden_services")
def test_review_matches__hidden_or_closed(mock_log_closed_or_hidden_services: MagicMock):
    # Arrange
    nhs_entity = NHSEntity(PHARMACY_STANDARD_EVENT)
    nhs_entity.org_status = "Closed"
    nhs_entity.org_type = "Pharmacy"
    nhs_entity.org_sub_type = "Pharmacy"
    service = dummy_dos_service()
    service.statusid = 1
    matching_services = [service]
    # Act
    response = review_matches(matching_services, nhs_entity)
    # Assert
    assert response is None
    mock_log_closed_or_hidden_services.assert_called_once_with(nhs_entity, matching_services)


@patch(f"{FILE_PATH}.log_invalid_open_times")
def test_review_matches__invalid_opening_times(mock_log_invalid_open_times: MagicMock) -> None:
    # Arrange
    change_event = PHARMACY_STANDARD_EVENT.copy()
    change_event["OpeningTimes"] = [
        {
            "Weekday": "Monday",
            "OpeningTime": "09:00",
            "ClosingTime": "13:00",
            "OpeningTimeType": "General",
            "AdditionalOpeningDate": "",
            "IsOpen": True,
        },
        {
            "Weekday": "Monday",
            "OpeningTime": "12:00",
            "ClosingTime": "17:30",
            "OpeningTimeType": "General",
            "AdditionalOpeningDate": "",
            "IsOpen": True,
        },
    ]
    nhs_entity = NHSEntity(change_event)
    service = dummy_dos_service()
    service.statusid = 1
    matching_services = [service]
    # Act
    response = review_matches(matching_services, nhs_entity)
    # Assert
    assert response == matching_services
    mock_log_invalid_open_times.assert_called_once_with(nhs_entity, matching_services)


@patch(f"{FILE_PATH}.log_missing_dos_service_for_a_given_type")
def test_check_for_missing_dos_services__missing(mock_log_missing_dos_service_for_a_given_type):
    # Arrange
    entity = MagicMock()
    entity.check_for_service.return_value = True
    service = dummy_dos_service()
    service.typeid = 13
    service.statusid = 1
    matching_dos_services = [service]
    # Act
    check_for_missing_dos_services(entity, matching_dos_services, BLOOD_PRESSURE)
    # Assert
    entity.check_for_service.assert_called_once_with(BLOOD_PRESSURE.NHS_UK_SERVICE_CODE)
    mock_log_missing_dos_service_for_a_given_type.assert_called_once_with(
        nhs_entity=entity,
        matching_services=matching_dos_services,
        missing_type=BLOOD_PRESSURE,
        reason="No 'Blood Pressure' type service profile",
    )


@patch(f"{FILE_PATH}.log_missing_dos_service_for_a_given_type")
def test_check_for_missing_dos_services__not_missing(mock_log_missing_dos_service_for_a_given_type, change_event):
    # Arrange
    entity = MagicMock()
    entity.check_for_service.return_value = True
    service = dummy_dos_service()
    service.typeid = 13
    service.statusid = 1
    service_two = dummy_dos_service()
    service_two.typeid = BLOOD_PRESSURE.DOS_TYPE_ID
    service_two.statusid = 1
    matching_dos_services = [service, service_two]

    # Act
    check_for_missing_dos_services(entity, matching_dos_services, BLOOD_PRESSURE)

    # Assert
    entity.check_for_service.assert_called_once_with(BLOOD_PRESSURE.NHS_UK_SERVICE_CODE)
    mock_log_missing_dos_service_for_a_given_type.assert_not_called()


@patch(f"{FILE_PATH}.log_missing_dos_service_for_a_given_type")
def test_check_for_missing_dos_services__not_on_nhs_entity(mock_log_missing_dos_service_for_a_given_type, change_event):
    # Arrange
    entity = MagicMock()
    entity.check_for_service.return_value = False
    service = dummy_dos_service()
    service.typeid = 13
    service.statusid = 1
    service_two = dummy_dos_service()
    service_two.typeid = BLOOD_PRESSURE.DOS_TYPE_ID
    service_two.statusid = 1
    matching_dos_services = [service, service_two]

    # Act
    check_for_missing_dos_services(entity, matching_dos_services, BLOOD_PRESSURE)

    # Assert
    entity.check_for_service.assert_called_once_with(BLOOD_PRESSURE.NHS_UK_SERVICE_CODE)
    mock_log_missing_dos_service_for_a_given_type.assert_not_called()


def test_remove_service_if_not_on_change_event() -> None:
    # Arrange
    service = dummy_dos_service()
    service.typeid = 13
    service.statusid = 1
    service2 = dummy_dos_service()
    service2.typeid = 148
    service2.statusid = 2
    matching_services = [service, service2]
    nhs_entity = NHSEntity(PHARMACY_STANDARD_EVENT)
    nhs_entity.blood_pressure = False
    # Act
    response = remove_service_if_not_on_change_event(matching_services, nhs_entity, "blood_pressure", BLOOD_PRESSURE)
    # Assert
    assert response == [service]


@patch(f"{FILE_PATH}.log_missing_dos_service")
def test_check_for_missing_palliative_care_service(mock_log_missing_dos_service: MagicMock) -> None:
    # Arrange
    service = dummy_dos_service()
    service.typeid = 131
    service.statusid = 1
    matching_services = [service]
    nhs_entity = NHSEntity(PHARMACY_STANDARD_EVENT)
    nhs_entity.palliative_care = True
    # Act
    check_for_missing_palliative_care_service(nhs_entity, matching_services)
    # Assert
    mock_log_missing_dos_service.assert_called_once_with(
        nhs_entity=nhs_entity,
        dos_service=service,
        missing_type=PALLIATIVE_CARE,
        reason="No Active Pharmacy with 5 Character ODSCode",
    )
