import json
from unittest.mock import MagicMock, patch

from aws_lambda_powertools.logging import Logger

from application.conftest import dummy_dos_service
from application.service_matcher.reporting import (
    HIDDEN_OR_CLOSED_REPORT_ID,
    INVALID_OPEN_TIMES_REPORT_ID,
    MISSING_SERVICE_TYPE_REPORT_ID,
    UNMATCHED_PHARMACY_REPORT_ID,
    log_closed_or_hidden_services,
    log_invalid_open_times,
    log_missing_dos_service_for_a_given_type,
    log_unmatched_nhsuk_service,
)
from common.commissioned_service_type import BLOOD_PRESSURE
from common.constants import PHARMACY_SERVICE_TYPE_ID
from common.nhs import NHSEntity


@patch.object(Logger, "warning")
def test_log_closed_or_hidden_services(mock_logger: MagicMock, change_event: dict[str, str]) -> None:
    # Arrange
    nhs_entity = NHSEntity(change_event)
    dos_service = dummy_dos_service()
    matching_services = [dos_service]
    # Act
    log_closed_or_hidden_services(nhs_entity, matching_services)
    # Assert
    assert (
        HIDDEN_OR_CLOSED_REPORT_ID == "HIDDEN_OR_CLOSED"
    ), f"Report ID should be HIDDEN_OR_CLOSED but was {HIDDEN_OR_CLOSED_REPORT_ID}"
    mock_logger.assert_called_with(
        "NHS Service marked as closed or hidden, no change events will be produced from this event",
        report_key=HIDDEN_OR_CLOSED_REPORT_ID,
        dos_service_uid=dos_service.uid,
        nhsuk_odscode=nhs_entity.odscode,
        dos_service_name=dos_service.name,
        nhsuk_service_status=nhs_entity.org_status,
        nhsuk_service_type=nhs_entity.org_type,
        nhsuk_sector=nhs_entity.org_sub_type,
        dos_service_status=dos_service.status_name,
        dos_service_type=dos_service.service_type_name,
        dos_region=dos_service.get_region(),
        nhsuk_parent_organisation_name=nhs_entity.parent_org_name,
        dos_service_typeid=dos_service.typeid,
    )


@patch.object(Logger, "warning")
def test_log_unmatched_nhsuk_service(mock_logger: MagicMock) -> None:
    # Arrange
    nhs_entity = NHSEntity(
        {
            "ODSCode": "SLC4X",
            "OrganisationName": "OrganisationName",
            "OrganisationTypeId": "PHA",
            "OrganisationStatus": "OrganisationStatus",
            "OrganisationSubType": "OrganisationSubType",
            "Address2": "address2",
            "Address3": "address3",
            "City": "city",
            "County": "country",
            "Postcode": "MK2 4AX",
        },
    )
    # Act
    log_unmatched_nhsuk_service(nhs_entity)
    # Assert
    assert (
        UNMATCHED_PHARMACY_REPORT_ID == "UNMATCHED_PHARMACY"
    ), f"Log ID should be UNMATCHED_PHARMACY but was {UNMATCHED_PHARMACY_REPORT_ID}"
    mock_logger.assert_called_with(
        f"No matching DOS services found that fit all criteria for ODSCode '{nhs_entity.odscode}'",
        report_key=UNMATCHED_PHARMACY_REPORT_ID,
        nhsuk_odscode=nhs_entity.odscode,
        nhsuk_organisation_name=nhs_entity.org_name,
        nhsuk_organisation_typeid=nhs_entity.org_type_id,
        nhsuk_organisation_status=nhs_entity.org_status,
        nhsuk_organisation_subtype=nhs_entity.org_sub_type,
        nhsuk_address1=nhs_entity.entity_data.get("Address1", ""),
        nhsuk_address2=nhs_entity.entity_data.get("Address2", ""),
        nhsuk_address3=nhs_entity.entity_data.get("Address3", ""),
        nhsuk_city=nhs_entity.entity_data.get("City", ""),
        nhsuk_county=nhs_entity.entity_data.get("County", ""),
        nhsuk_postcode=nhs_entity.postcode,
        nhsuk_parent_organisation_name=nhs_entity.parent_org_name,
    )


@patch.object(Logger, "warning")
def test_log_invalid_open_times(mock_logger: MagicMock) -> None:
    # Arrange
    opening_times = [
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
    nhs_entity = NHSEntity({"OpeningTimes": opening_times})
    nhs_entity.odscode = "SLC4X"
    nhs_entity.org_name = "OrganisationName"

    dos_services = [dummy_dos_service() for _ in range(3)]
    # Act
    log_invalid_open_times(nhs_entity, dos_services)
    # Assert
    mock_logger.assert_called_with(
        f"NHS Entity '{nhs_entity.odscode}' has a misformatted or illogical set of opening times.",
        report_key=INVALID_OPEN_TIMES_REPORT_ID,
        nhsuk_odscode=nhs_entity.odscode,
        nhsuk_organisation_name=nhs_entity.org_name,
        nhsuk_open_times_payload=json.dumps(nhs_entity.entity_data["OpeningTimes"]),
        dos_service_type_name=", ".join(str(service.service_type_name) for service in dos_services),
        dos_services=", ".join(str(service.uid) for service in dos_services),
        environment="local",
        cloudwatch_metric_filter_matching_attribute="InvalidOpenTimes",
    )


@patch.object(Logger, "warning")
def test_log_missing_dos_service_for_a_given_type(mock_logger: MagicMock) -> None:
    dos_service = dummy_dos_service()
    dos_service.typeid = PHARMACY_SERVICE_TYPE_ID
    dos_service.statusid = 1
    reason = "reason 123"
    nhs_entity = NHSEntity(
        {"Address1": "address1", "Address2": "address2", "Address3": "address3", "City": "city", "County": "county"},
    )
    nhs_entity.odscode = "SLC4X"
    nhs_entity.org_name = "OrganisationName"
    nhs_entity.org_type_id = "PHA"
    nhs_entity.org_status = "OrganisationStatus"
    nhs_entity.org_sub_type = "OrganisationSubType"
    nhs_entity.postcode = "MK2 XXX"
    log_missing_dos_service_for_a_given_type(nhs_entity, [dos_service], BLOOD_PRESSURE, reason)
    assert MISSING_SERVICE_TYPE_REPORT_ID == "MISSING_SERVICE_TYPE"
    mock_logger.assert_called_with(
        "Missing DoS service for a certain type associated with a NHS UK Service Code",
        report_key=MISSING_SERVICE_TYPE_REPORT_ID,
        nhsuk_odscode=nhs_entity.odscode,
        nhsuk_organisation_name=nhs_entity.org_name,
        nhsuk_organisation_typeid=nhs_entity.org_type_id,
        nhsuk_organisation_status=nhs_entity.org_status,
        nhsuk_organisation_subtype=nhs_entity.org_sub_type,
        dos_missing_service_type=BLOOD_PRESSURE.TYPE_NAME,
        dos_service_address=dos_service.address,
        dos_service_postcode=dos_service.postcode,
        dos_region=dos_service.get_region(),
        reason=reason,
        nhsuk_parent_organisation_name=nhs_entity.parent_org_name,
    )


@patch.object(Logger, "warning")
def test_log_missing_dos_service_for_a_given_type__no_active_dos_services(mock_logger: MagicMock) -> None:
    dos_service = dummy_dos_service()
    dos_service.statusid = 3
    reason = "reason 123"
    nhs_entity = NHSEntity(
        {"Address1": "address1", "Address2": "address2", "Address3": "address3", "City": "city", "County": "county"},
    )
    nhs_entity.odscode = "SLC4X"
    nhs_entity.org_name = "OrganisationName"
    nhs_entity.org_type_id = "PHA"
    nhs_entity.org_status = "OrganisationStatus"
    nhs_entity.org_sub_type = "OrganisationSubType"
    nhs_entity.postcode = "MK2 XXX"
    log_missing_dos_service_for_a_given_type(nhs_entity, [dos_service], BLOOD_PRESSURE, reason)
    assert MISSING_SERVICE_TYPE_REPORT_ID == "MISSING_SERVICE_TYPE"
    mock_logger.assert_not_called()
