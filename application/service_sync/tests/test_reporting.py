from os import environ
from unittest.mock import MagicMock, patch

from aws_lambda_powertools.logging import Logger

from application.conftest import dummy_dos_service
from application.service_sync.reporting import (
    BLANK_STANDARD_OPENINGS_REPORT_ID,
    GENERIC_BANK_HOLIDAY_REPORT_ID,
    GENERIC_CHANGE_EVENT_ERROR_REPORT_ID,
    INVALID_POSTCODE_REPORT_ID,
    SERVICE_UPDATE_REPORT_ID,
    log_blank_standard_opening_times,
    log_invalid_nhsuk_postcode,
    log_service_updated,
    log_service_with_generic_bank_holiday,
    log_website_is_invalid,
)
from common.nhs import NHSEntity
from common.opening_times import OpenPeriod


@patch.object(Logger, "warning")
def test_log_blank_standard_opening_times(mock_logger, change_event):
    # Arrange
    nhs_entity = NHSEntity(change_event)
    dos_service = dummy_dos_service()
    dos_service.region = "London"
    # Act
    log_blank_standard_opening_times(nhs_entity, dos_service)
    # Assert
    assert (
        BLANK_STANDARD_OPENINGS_REPORT_ID == "BLANK_STANDARD_OPENINGS"
    ), f"Report ID should be BLANK_STANDARD_OPENINGS but was {BLANK_STANDARD_OPENINGS_REPORT_ID}"
    mock_logger.assert_called_with(
        "NHS Service has matching DoS services but no given standard opening times.",
        report_key=BLANK_STANDARD_OPENINGS_REPORT_ID,
        nhsuk_odscode=nhs_entity.odscode,
        dos_service_id=dos_service.id,
        dos_service_uid=dos_service.uid,
        dos_service_name=dos_service.name,
        nhsuk_service_status=nhs_entity.org_status,
        nhsuk_service_type=nhs_entity.org_type,
        nhsuk_sector=nhs_entity.org_sub_type,
        dos_service_status=dos_service.statusid,
        dos_service_type=dos_service.typeid,
        dos_service_type_name=dos_service.service_type_name,
        dos_region=dos_service.get_region(),
    )


@patch.object(Logger, "warning")
def test_log_invalid_nhsuk_postcode(mock_logger):
    # Arrange
    environ["ENV"] = "dev"
    county = "county"
    city = "city"
    nhs_entity = NHSEntity(
        {"Address1": "address1", "Address2": "address2", "Address3": "address3", "City": city, "County": county},
    )
    nhs_entity.odscode = "SLC4X"
    nhs_entity.org_name = "OrganisationName"
    nhs_entity.org_type_id = "PHA"
    nhs_entity.org_status = "OrganisationStatus"
    nhs_entity.org_sub_type = "OrganisationSubType"
    nhs_entity.postcode = "MK2 XXX"

    dos_service = dummy_dos_service()
    # Act
    log_invalid_nhsuk_postcode(nhs_entity, dos_service)
    # Assert
    assert (
        INVALID_POSTCODE_REPORT_ID == "INVALID_POSTCODE"
    ), f"Log ID should be INVALID_POSTCODE but was {INVALID_POSTCODE_REPORT_ID}"
    mock_logger.assert_called_with(
        f"NHS entity '{nhs_entity.odscode}' postcode '{nhs_entity.postcode}' is not a valid DoS postcode!",
        report_key=INVALID_POSTCODE_REPORT_ID,
        nhsuk_odscode=nhs_entity.odscode,
        nhsuk_organisation_type=nhs_entity.org_type,
        nhsuk_organisation_name=nhs_entity.org_name,
        nhsuk_organisation_subtype=nhs_entity.org_sub_type,
        nhsuk_address1=nhs_entity.entity_data.get("Address1", ""),
        nhsuk_address2=nhs_entity.entity_data.get("Address2", ""),
        nhsuk_address3=nhs_entity.entity_data.get("Address3", ""),
        nhsuk_city=nhs_entity.entity_data.get("City", ""),
        nhsuk_county=nhs_entity.entity_data.get("County", ""),
        nhsuk_postcode=nhs_entity.postcode,
        validation_error_reason="Postcode not valid/found on DoS",
        dos_service=dos_service.uid,
        dos_service_type_name=dos_service.service_type_name,
        dos_region=dos_service.get_region(),
        dos_service_name=dos_service.name,
    )
    # Clean up
    del environ["ENV"]


@patch.object(Logger, "warning")
def test_log_service_with_generic_bank_holiday(mock_logger):
    # Arrange
    nhs_entity = NHSEntity({})
    nhs_entity.odscode = "SLC4X"
    nhs_entity.org_name = "OrganisationName"
    dos_service = dummy_dos_service()
    open_periods = [OpenPeriod.from_string("08:00-13:00"), OpenPeriod.from_string("04:00-18:00")]
    dos_service.standard_opening_times.generic_bankholiday = open_periods
    # Act
    log_service_with_generic_bank_holiday(nhs_entity, dos_service)
    # Assert
    mock_logger.assert_called_with(
        f"DoS Service uid={dos_service.uid} has a generic BankHoliday Standard opening time set in DoS",
        report_key=GENERIC_BANK_HOLIDAY_REPORT_ID,
        nhsuk_odscode=nhs_entity.odscode,
        nhsuk_organisation_name=nhs_entity.org_name,
        dos_service_uid=dos_service.uid,
        dos_service_name=dos_service.name,
        bank_holiday_opening_times=OpenPeriod.list_string(open_periods),
        nhsuk_parent_org=nhs_entity.parent_org_name,
        dos_service_type_name=dos_service.service_type_name,
        dos_region=dos_service.get_region(),
    )


@patch.object(Logger, "warning")
def test_log_website_is_invalid(mock_logger: MagicMock):
    # Arrange
    nhs_entity = NHSEntity({})
    nhs_entity.website = nhs_website = "http://www.google.com"
    dos_service = dummy_dos_service()
    # Act
    log_website_is_invalid(nhs_entity, nhs_website, dos_service)
    # Assert
    mock_logger.assert_called_with(
        "Website is not valid",
        report_key=GENERIC_CHANGE_EVENT_ERROR_REPORT_ID,
        error_reason="Website is not valid",
        error_info=f"NHSUK unedited website: '{nhs_entity.website}', NHSUK website='{nhs_website}'",
        dos_region=dos_service.get_region(),
        extra={
            "nhs_unedited_website": nhs_entity.website,
            "nhs_website": nhs_website,
        },
    )


@patch.object(Logger, "warning")
def test_log_service_updated(mock_logger: MagicMock):
    # Arrange
    action = "action"
    data_field_modified = "data_field_modified"
    new_value = "new_value"
    previous_value = "previous_value"
    service_name = "ServiceName"
    service_uid = "1234567890"
    type_id = "1"
    dos_service = dummy_dos_service()
    # Act
    log_service_updated(
        action=action,
        data_field_modified=data_field_modified,
        new_value=new_value,
        previous_value=previous_value,
        service_name=service_name,
        service_uid=service_uid,
        type_id=type_id,
        dos_service=dos_service,
    )
    # Assert
    assert SERVICE_UPDATE_REPORT_ID == "SERVICE_UPDATE"
    mock_logger.assert_called_with(
        "Service update complete",
        extra={
            "report_key": SERVICE_UPDATE_REPORT_ID,
            "action": action,
            "previous_value": previous_value,
            "new_value": new_value,
            "data_field_modified": data_field_modified,
            "service_name": service_name,
            "service_uid": service_uid,
            "type_id": type_id,
            "dos_region": dos_service.get_region(),
        },
    )
