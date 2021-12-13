from unittest.mock import patch

from aws_lambda_powertools import Logger
from ..dos import VALID_STATUS_ID
from ..nhs import NHSEntity
from ..reporting import report_closed_or_hidden_services, HIDDEN_OR_CLOSED_REPORT_ID
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
