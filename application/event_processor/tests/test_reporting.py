from unittest.mock import patch

from aws_lambda_powertools import Logger
from ..dos import VALID_STATUS_ID
from ..nhs import NHSEntity
from ..reporting import (
    report_closed_or_hidden_services,
    log_unmatched_nhsuk_pharmacies,
    HIDDEN_OR_CLOSED_REPORT_ID,
    UN_MATCHED_PHARMACY_REPORT_ID,
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
            "nhs_uk_odscode": nhs_entity.ODSCode,
            "dos_publicname": dos_service.publicname,
            "nhs_uk_service_status": nhs_entity.OrganisationStatus,
            "nhs_uk_service_type": nhs_entity.OrganisationType,
            "nhs_uk_service_sub_sector": nhs_entity.OrganisationSubType,
            "dos_service_status": VALID_STATUS_ID,
            "dos_service_type": dos_service.typeid,
        },
    )


@patch.object(Logger, "warning")
def test_log_unmatched_nhsuk_pharmacies(mock_logger):
    # Arrange
    nhs_entity = NHSEntity({})
    nhs_entity.ODSCode = "SLC4X"
    nhs_entity.OrganisationName = "OrganisationName"
    nhs_entity.ServiceType = "PHA"
    nhs_entity.OrganisationStatus = "OrganisationStatus"
    nhs_entity.OrganisationSubType = "OrganisationSubType"
    nhs_entity.Address2 = "address2"
    nhs_entity.Address3 = "address3"
    nhs_entity.Address4 = "address4"
    nhs_entity.Postcode = "MK2 4AX"
    # Act
    log_unmatched_nhsuk_pharmacies(nhs_entity)
    # Assert
    assert (
        UN_MATCHED_PHARMACY_REPORT_ID == "UN_MATCHED_PHARMACY"
    ), f"Log ID should be UN_MATCHED_PHARMACY but was {UN_MATCHED_PHARMACY_REPORT_ID}"
    mock_logger.assert_called_with(
        f"No matching DOS services found that fit all " f"criteria for ODSCode '{nhs_entity.ODSCode}'",
        extra={
            "report_key": UN_MATCHED_PHARMACY_REPORT_ID,
            "nhsuk_odscode": nhs_entity.ODSCode,
            "nhsuk_org_name": nhs_entity.OrganisationName,
            "nhsuk_service_type": nhs_entity.ServiceType,
            "nhsuk_service_status": nhs_entity.OrganisationStatus,
            "nhsuk_service_sub_sector": nhs_entity.OrganisationSubType,
            "nhsuk_address1": "",
            "nhsuk_address2": nhs_entity.Address2,
            "nhsuk_address3": nhs_entity.Address3,
            "nhsuk_address4": nhs_entity.Address4,
            "nhsuk_address5": "",
            "nhsuk_postcode": nhs_entity.Postcode,
        },
    )
