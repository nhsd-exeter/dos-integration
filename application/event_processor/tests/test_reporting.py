from unittest.mock import patch
import json

from aws_lambda_powertools import Logger
from ...common.dos import VALID_STATUS_ID
from ..nhs import NHSEntity
from ..reporting import (
    INVALID_OPEN_TIMES_REPORT_ID,
    log_invalid_open_times,
    report_closed_or_hidden_services,
    log_unmatched_nhsuk_pharmacies,
    log_invalid_nhsuk_pharmacy_postcode,
    HIDDEN_OR_CLOSED_REPORT_ID,
    UN_MATCHED_PHARMACY_REPORT_ID,
    INVALID_POSTCODE_REPORT_ID,
)
from .conftest import dummy_dos_service


@patch.object(Logger, "warning")
def test_report_closed_or_hidden_services(mock_logger, change_event):
    # Arrange
    nhs_entity = NHSEntity(change_event)
    dos_service = dummy_dos_service()
    matching_services = [dos_service]
    # Act
    report_closed_or_hidden_services(nhs_entity, matching_services)
    # Assert
    assert (
        HIDDEN_OR_CLOSED_REPORT_ID == "HIDDEN_OR_CLOSED"
    ), f"Report ID should be HIDDEN_OR_CLOSED but was {HIDDEN_OR_CLOSED_REPORT_ID}"
    mock_logger.assert_called_with(
        "NHS Service marked as closed or hidden, no change requests will be produced from this event",
        extra={
            "report_key": HIDDEN_OR_CLOSED_REPORT_ID,
            "dos_service_id": dos_service.id,
            "dos_service_uid": dos_service.uid,
            "nhsuk_odscode": nhs_entity.odscode,
            "dos_publicname": dos_service.publicname,
            "nhsuk_service_status": nhs_entity.org_status,
            "nhsuk_service_type": nhs_entity.org_type,
            "nhsuk_sector": nhs_entity.org_sub_type,
            "dos_service_status": VALID_STATUS_ID,
            "dos_service_type": dos_service.typeid,
        },
    )


@patch.object(Logger, "warning")
def test_log_unmatched_nhsuk_pharmacies(mock_logger):
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
        }
    )
    # Act
    log_unmatched_nhsuk_pharmacies(nhs_entity)
    # Assert
    assert (
        UN_MATCHED_PHARMACY_REPORT_ID == "UN_MATCHED_PHARMACY"
    ), f"Log ID should be UN_MATCHED_PHARMACY but was {UN_MATCHED_PHARMACY_REPORT_ID}"
    mock_logger.assert_called_with(
        f"No matching DOS services found that fit all criteria for ODSCode '{nhs_entity.odscode}'",
        extra={
            "report_key": UN_MATCHED_PHARMACY_REPORT_ID,
            "nhsuk_odscode": nhs_entity.odscode,
            "nhsuk_organisation_name": nhs_entity.org_name,
            "nhsuk_organisation_typeid": nhs_entity.org_type_id,
            "nhsuk_organisation_status": nhs_entity.org_status,
            "nhsuk_organisation_subtype": nhs_entity.org_sub_type,
            "nhsuk_address1": nhs_entity.entity_data.get("Address1", ""),
            "nhsuk_address2": nhs_entity.entity_data.get("Address2", ""),
            "nhsuk_address3": nhs_entity.entity_data.get("Address3", ""),
            "nhsuk_city": nhs_entity.entity_data.get("City", ""),
            "nhsuk_county": nhs_entity.entity_data.get("County", ""),
            "nhsuk_postcode": nhs_entity.postcode,
            "nhsuk_parent_organisation_name": nhs_entity.parent_org_name,
        },
    )


@patch.object(Logger, "warning")
def test_log_invalid_nhsuk_pharmacy_postcode(mock_logger):
    # Arrange
    nhs_entity = NHSEntity(
        {"Address1": "address1", "Address2": "address2", "Address3": "address3", "City": "city", "County": "county"}
    )
    nhs_entity.odscode = "SLC4X"
    nhs_entity.org_name = "OrganisationName"
    nhs_entity.org_type_id = "PHA"
    nhs_entity.org_status = "OrganisationStatus"
    nhs_entity.org_sub_type = "OrganisationSubType"
    nhs_entity.postcode = "MK2 XXX"

    dos_service = dummy_dos_service()
    # Act
    log_invalid_nhsuk_pharmacy_postcode(nhs_entity, dos_service)
    # Assert
    assert (
        INVALID_POSTCODE_REPORT_ID == "INVALID_POSTCODE"
    ), f"Log ID should be INVALID_POSTCODE but was {INVALID_POSTCODE_REPORT_ID}"
    mock_logger.assert_called_with(
        f"NHS entity '{nhs_entity.odscode}' postcode '{nhs_entity.postcode}' is not a valid DoS postcode!",
        extra={
            "report_key": INVALID_POSTCODE_REPORT_ID,
            "nhsuk_odscode": nhs_entity.odscode,
            "nhsuk_organisation_name": nhs_entity.org_name,
            "nhsuk_address1": nhs_entity.address_lines[0],
            "nhsuk_address2": nhs_entity.address_lines[1],
            "nhsuk_address3": nhs_entity.address_lines[2],
            "nhsuk_city": nhs_entity.city,
            "nhsuk_postcode": nhs_entity.postcode,
            "nhsuk_county": nhs_entity.county,
            "validation_error_reason": "Postcode not valid/found on DoS",
            "dos_service": dos_service.uid,
        },
    )


@patch.object(Logger, "warning")
def test_log_invalid_open_times(mock_logger):
    # Arrange
    opening_times = [
        {
            "Weekday": "Monday",
            "Times": "09:00-13:00",
            "OpeningTimeType": "General",
            "AdditionalOpeningDate": "",
            "IsOpen": True,
        },
        {
            "Weekday": "Monday",
            "Times": "12:00-17:30",
            "OpeningTimeType": "General",
            "AdditionalOpeningDate": "",
            "IsOpen": True,
        },
    ]
    nhs_entity = NHSEntity({"OpeningTimes": opening_times})
    nhs_entity.odscode = "SLC4X"
    nhs_entity.org_name = "OrganisationName"

    dos_services = [dummy_dos_service() for i in range(3)]
    # Act
    log_invalid_open_times(nhs_entity, dos_services)
    # Assert
    mock_logger.assert_called_with(
        f"NHS Entity '{nhs_entity.odscode}' has a misformatted or illogical set of opening times.",
        extra={
            "report_key": INVALID_OPEN_TIMES_REPORT_ID,
            "nhsuk_odscode": nhs_entity.odscode,
            "nhsuk_organisation_name": nhs_entity.org_name,
            "nhsuk_open_times_payload": json.dumps(opening_times),
            "dos_services": ", ".join(str(service.uid) for service in dos_services),
        },
    )
