from typing import List

from aws_lambda_powertools.logging.logger import Logger
from dos import DoSService, VALID_STATUS_ID
from nhs import NHSEntity

HIDDEN_OR_CLOSED_REPORT_ID = "HIDDEN_OR_CLOSED"

logger = Logger(child=True)


def report_closed_or_hidden_services(nhs_entity: NHSEntity, matching_services: List[DoSService]) -> None:
    """Report closed or hidden NHS UK services

    Args:
        nhs_entity (NHSEntity): The NHS entity to report
        matching_services (List[DoSService]): The list of DoS matching services
    """
    for dos_service in matching_services:
        logger.warning(
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
