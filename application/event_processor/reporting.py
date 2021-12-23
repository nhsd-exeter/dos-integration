from typing import List
from aws_lambda_powertools.logging.logger import Logger
from dos import DoSService, VALID_STATUS_ID
from nhs import NHSEntity

HIDDEN_OR_CLOSED_REPORT_ID = "HIDDEN_OR_CLOSED"
UN_MATCHED_PHARMACY_REPORT_ID = "UN_MATCHED_PHARMACY"
INVALID_POSTCODE_REPORT_ID = "INVALID_POSTCODE"

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
                "nhsuk_odscode": nhs_entity.odscode,
                "dos_publicname": dos_service.publicname,
                "nhsuk_service_status": nhs_entity.org_status,
                "nhsuk_service_type": nhs_entity.org_type,
                "nhsuk_sector": nhs_entity.org_sub_type,
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
            "nhsuk_parent_organisation_name": nhs_entity.parent_org_name
        },
    )


def log_invalid_nhsuk_pharmacy_postcode(nhs_entity: NHSEntity, dos_service: DoSService) -> None:
    """Log invalid NHS pharmacy postcode
    Args:
        nhs_entity (NHSEntity): The NHS entity to report
        dos_service (List[DoSService]): The list of DoS matching services
    """

    logger.warning(
        f"NHS postcode '{nhs_entity.Postcode}' is not a valid DoS postcode!"
        f"criteria for ODSCode '{nhs_entity.ODSCode}'",
        extra={
            "report_key": INVALID_POSTCODE_REPORT_ID,
            "nhsuk_odscode": nhs_entity.ODSCode,
            "nhsuk_organisation_name": nhs_entity.OrganisationName,
            "nhsuk_address1": nhs_entity.Address1 if hasattr(nhs_entity, "Address1") else "",
            "nhsuk_address2": nhs_entity.Address2 if hasattr(nhs_entity, "Address2") else "",
            "nhsuk_address3": nhs_entity.Address3 if hasattr(nhs_entity, "Address3") else "",
            "nhsuk_city": nhs_entity.City if hasattr(nhs_entity, "City") else "",
            "nhsuk_county": nhs_entity.County if hasattr(nhs_entity, "County") else "",
            "nhsuk_postcode": nhs_entity.Postcode,
            "validation_error_reason": "Postcode not valid/found on DoS",
            "dos_services": dos_service.uid,
        },
    )
