import json
from os import environ
from typing import Any

from aws_embedded_metrics import metric_scope
from aws_lambda_powertools.logging.logger import Logger

from common.commissioned_service_type import CommissionedServiceType
from common.constants import DOS_ACTIVE_STATUS_ID, PHARMACY_SERVICE_TYPE_ID
from common.dos import DoSService
from common.nhs import NHSEntity

logger = Logger(child=True)

HIDDEN_OR_CLOSED_REPORT_ID = "HIDDEN_OR_CLOSED"
UNMATCHED_PHARMACY_REPORT_ID = "UNMATCHED_PHARMACY"
INVALID_OPEN_TIMES_REPORT_ID = "INVALID_OPEN_TIMES"
UNMATCHED_SERVICE_TYPE_REPORT_ID = "UNMATCHED_SERVICE_TYPE"
UNEXPECTED_PHARMACY_PROFILING_REPORT_ID = "UNEXPECTED_PHARMACY_PROFILING"
MISSING_SERVICE_TYPE_REPORT_ID = "MISSING_SERVICE_TYPE"


def log_closed_or_hidden_services(
    nhs_entity: NHSEntity,
    matching_services: list[DoSService],
) -> None:
    """Log closed or hidden NHS UK services.

    Args:
        nhs_entity (NHSEntity): The NHS entity to report
        matching_services (List[DoSService]): The list of DoS matching services
    """
    for dos_service in matching_services:
        logger.warning(
            "NHS Service marked as closed or hidden, no change events will be produced from this event",
            extra={
                "report_key": HIDDEN_OR_CLOSED_REPORT_ID,
                "dos_service_uid": dos_service.uid,
                "nhsuk_odscode": nhs_entity.odscode,
                "dos_service_name": dos_service.name,
                "nhsuk_service_status": nhs_entity.org_status,
                "nhsuk_service_type": nhs_entity.org_type,
                "nhsuk_sector": nhs_entity.org_sub_type,
                "dos_service_status": dos_service.status_name,
                "dos_service_type": dos_service.service_type_name,
                "dos_region": dos_service.get_region(),
                "nhsuk_parent_organisation_name": nhs_entity.parent_org_name,
                "dos_service_typeid": dos_service.typeid,
            },
        )


def log_unmatched_nhsuk_service(nhs_entity: NHSEntity) -> None:
    """Log unmatched NHS Services.

    Args:
        nhs_entity (NHSEntity): NHS entity to log.
    """
    logger.warning(
        f"No matching DOS services found that fit all criteria for ODSCode '{nhs_entity.odscode}'",
        extra={
            "report_key": UNMATCHED_PHARMACY_REPORT_ID,
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


@metric_scope
def log_invalid_open_times(
    nhs_entity: NHSEntity,
    matching_services: list[DoSService],
    metrics: Any,  # noqa: ANN401
) -> None:
    """Report invalid open times for nhs entity.

    Args:
        nhs_entity (NHSEntity): The NHS entity to report
        matching_services (List[DoSService]): The list of DoS matching services
        metrics (Any): The metrics object to report to.
    """
    error_msg = f"NHS Entity '{nhs_entity.odscode}' has a misformatted or illogical set of opening times."
    logger.warning(
        error_msg,
        extra={
            "report_key": INVALID_OPEN_TIMES_REPORT_ID,
            "nhsuk_odscode": nhs_entity.odscode,
            "nhsuk_organisation_name": nhs_entity.org_name,
            "nhsuk_open_times_payload": json.dumps(
                nhs_entity.entity_data["OpeningTimes"],
            ),
            "dos_service_type_name": ", ".join(str(service.service_type_name) for service in matching_services),
            "dos_services": ", ".join(str(service.uid) for service in matching_services),
        },
    )
    metrics.set_namespace("UEC-DOS-INT")
    metrics.set_property("level", "WARNING")
    metrics.set_property("message", error_msg)
    metrics.set_dimensions({"ENV": environ["ENV"]})
    metrics.put_metric("InvalidOpenTimes", 1, "Count")


def log_unmatched_service_types(
    nhs_entity: NHSEntity,
    unmatched_services: list[DoSService],
) -> None:
    """Log unmatched DOS service types.

    Args:
        nhs_entity (NHSEntity): The NHS entity to report
        unmatched_services (List[DoSService]): The list of DoS unmatched services.
    """
    for unmatched_service in unmatched_services:
        logger.warning(
            f"NHS entity '{nhs_entity.odscode}' service type '{ unmatched_service.typeid}' is not valid!",
            extra={
                "report_key": UNMATCHED_SERVICE_TYPE_REPORT_ID,
                "nhsuk_odscode": nhs_entity.odscode,
                "nhsuk_organisation_name": nhs_entity.org_name,
                "nhsuk_organisation_typeid": nhs_entity.org_type_id,
                "nhsuk_organisation_status": nhs_entity.org_status,
                "nhsuk_organisation_subtype": nhs_entity.org_sub_type,
                "nhsuk_parent_organisation_name": nhs_entity.parent_org_name,
                "dos_service_uid": unmatched_service.uid,
                "dos_service_id": unmatched_service.id,
                "dos_service_publicname": unmatched_service.name,
                "dos_service_status": DOS_ACTIVE_STATUS_ID,
                "dos_service_typeid": unmatched_service.typeid,
                "dos_service_type_name": unmatched_service.service_type_name,
            },
        )


def log_unexpected_pharmacy_profiling(
    nhs_entity: NHSEntity,
    matching_services: list[DoSService],
    reason: str,
) -> None:
    """Log a service found to have an invalid website.

    Args:
        nhs_entity (NHSEntity): The NHS entity to report
        matching_services (list[DoSService]): The DoS services to report
        reason (str): The reason for the report
    """
    for service in matching_services:
        logger.warning(
            "Pharmacy profiling is incorrect",
            extra={
                "report_key": UNEXPECTED_PHARMACY_PROFILING_REPORT_ID,
                "dos_service_uid": service.uid,
                "dos_service_name": service.name,
                "dos_service_address": service.address,
                "dos_service_postcode": service.postcode,
                "dos_service_type": service.service_type_name,
                "dos_region": service.get_region(),
                "reason": reason,
                "nhsuk_parent_organisation_name": nhs_entity.parent_org_name,
            },
        )


def log_missing_dos_service_for_a_given_type(
    nhs_entity: NHSEntity,
    matching_services: list[DoSService],
    missing_type: CommissionedServiceType,
    reason: str,
) -> None:
    """Reports when a Change Event has a Service Code defined and there isn't a corresponding DoS service.

    Args:
        nhs_entity (NHSEntity): The NHS entity to report
        matching_services (list[DoSService]): The DoS services to report
        missing_type (ServiceType): The subtype being reported as missing descriptors
        reason (str): The reason for the report
    """
    active_pharmacy_service = None
    for service in matching_services:
        if service.statusid == DOS_ACTIVE_STATUS_ID and service.typeid == PHARMACY_SERVICE_TYPE_ID:
            active_pharmacy_service = service

    if active_pharmacy_service is None:
        return

    logger.warning(
        "Missing DoS service for a certain type associated with a NHS UK Service Code",
        extra={
            "report_key": MISSING_SERVICE_TYPE_REPORT_ID,
            "nhsuk_odscode": nhs_entity.odscode,
            "nhsuk_organisation_name": nhs_entity.org_name,
            "nhsuk_organisation_typeid": nhs_entity.org_type_id,
            "nhsuk_organisation_status": nhs_entity.org_status,
            "nhsuk_organisation_subtype": nhs_entity.org_sub_type,
            "dos_missing_service_type": missing_type.TYPE_NAME,
            "dos_service_address": active_pharmacy_service.address,
            "dos_service_postcode": active_pharmacy_service.postcode,
            "dos_region": active_pharmacy_service.get_region(),
            "reason": reason,
            "nhsuk_parent_organisation_name": nhs_entity.parent_org_name,
        },
    )
