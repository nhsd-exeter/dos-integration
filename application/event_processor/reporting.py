from typing import List
from aws_lambda_powertools.logging.logger import Logger
from dos import DoSService, VALID_STATUS_ID
from nhs import NHSEntity

HIDDEN_OR_CLOSED_REPORT_ID = "HIDDEN_OR_CLOSED"
UN_MATCHED_PHARMACY_REPORT_ID = "UN_MATCHED_PHARMACY"

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


def log_unmatched_nhsuk_pharmacies(nhs_entity: NHSEntity) -> None:
    """Log unmatched NHS Pharmacies
    Args:
        nhs_entity (NHSEntity): NHS entity to log
    """

    logger.warning(
        f"No matching DOS services found that fit all " f"criteria for ODSCode '{nhs_entity.ODSCode}'",
        extra={
            "report_key": UN_MATCHED_PHARMACY_REPORT_ID,
            "nhsuk_odscode": nhs_entity.ODSCode,
            "nhsuk_org_name": nhs_entity.OrganisationName,
            "nhsuk_service_type": nhs_entity.ServiceType,
            "nhsuk_service_status": nhs_entity.OrganisationStatus,
            "nhsuk_service_sub_sector": nhs_entity.OrganisationSubType,
            "nhsuk_address1": nhs_entity.Address1 if hasattr(nhs_entity, "Address1") else "",
            "nhsuk_address2": nhs_entity.Address2 if hasattr(nhs_entity, "Address2") else "",
            "nhsuk_address3": nhs_entity.Address3 if hasattr(nhs_entity, "Address3") else "",
            "nhsuk_address4": nhs_entity.Address4 if hasattr(nhs_entity, "Address4") else "",
            "nhsuk_address5": nhs_entity.Address5 if hasattr(nhs_entity, "Address5") else "",
            "nhsuk_postcode": nhs_entity.Postcode,
        },
    )
