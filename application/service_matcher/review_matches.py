from aws_lambda_powertools.logging import Logger

from .reporting import (
    log_closed_or_hidden_services,
    log_invalid_open_times,
    log_missing_dos_service_for_a_given_type,
    log_unmatched_nhsuk_service,
)
from common.commissioned_service_type import BLOOD_PRESSURE, CONTRACEPTION, PALLIATIVE_CARE, CommissionedServiceType
from common.constants import DOS_ACTIVE_STATUS_ID, MAIN_PHARMACY_ODSCODE_LENGTH
from common.dos import DoSService
from common.nhs import NHSEntity

logger = Logger(child=True)


def review_matches(matching_services: list[DoSService], nhs_entity: NHSEntity) -> list[DoSService] | None:
    """Review and validate the matches and log any issues.

    Args:
        matching_services (list[DoSService]): The list of matching DoS services.
        nhs_entity (NHSEntity): The NHS entity to report

    Returns:
        list[DoSService]: The list of matching DoS services.
    """
    if not matching_services or not next(
        (True for service in matching_services if service.statusid == DOS_ACTIVE_STATUS_ID),
        False,
    ):
        log_unmatched_nhsuk_service(nhs_entity)
        return None

    remove_service_if_not_on_change_event(
        matching_services=matching_services,
        nhs_entity=nhs_entity,
        nhs_uk_key="blood_pressure",
        service_type=BLOOD_PRESSURE,
    )

    remove_service_if_not_on_change_event(
        matching_services=matching_services,
        nhs_entity=nhs_entity,
        nhs_uk_key="contraception",
        service_type=CONTRACEPTION,
    )

    logger.info("Matched DoS Services after services filtered", matched=matching_services)

    if nhs_entity.is_status_hidden_or_closed():
        log_closed_or_hidden_services(nhs_entity, matching_services)
        return None

    if not nhs_entity.all_times_valid():
        log_invalid_open_times(nhs_entity, matching_services)

    # Check for correct pharmacy profiling
    dos_matching_service_types = [service.typeid for service in matching_services]
    logger.debug(f"Matched service types: {dos_matching_service_types}", matched=matching_services)

    check_for_missing_dos_services(nhs_entity, matching_services, BLOOD_PRESSURE)
    check_for_missing_dos_services(nhs_entity, matching_services, CONTRACEPTION)
    check_for_missing_palliative_care_service(nhs_entity, matching_services)
    return matching_services


def remove_service_if_not_on_change_event(
    matching_services: list[DoSService],
    nhs_entity: NHSEntity,
    nhs_uk_key: str,
    service_type: CommissionedServiceType,
) -> list[DoSService]:
    """Removes a service from the matching services list if it is not on the change event.

    Args:
        matching_services (list[DoSService]): The list of matching services
        nhs_entity (NHSEntity): The nhs entity to check for the service
        nhs_uk_key (str): The key to check for the service on the nhs entity
        service_type (CommissionedServiceType): Various constants for the service type

    Returns:
        list[DoSService]: The list of matching services with the service removed if it is not on the change event
    """
    if remove_matched_services := [
        service
        for service in matching_services
        if service.statusid != DOS_ACTIVE_STATUS_ID
        and not getattr(nhs_entity, nhs_uk_key)
        and service.typeid == service_type.DOS_TYPE_ID
    ]:
        for service in remove_matched_services:
            matching_services.remove(service)
        logger.info(
            f"Removing matched {service_type.TYPE_NAME.lower()} services",
            remove_matched_services=remove_matched_services,
            matched=matching_services,
        )
    return matching_services


def check_for_missing_dos_services(
    nhs_entity: NHSEntity,
    matching_services: list[DoSService],
    service_type: CommissionedServiceType,
) -> None:
    """Logs when a Change Event has a Service Code defined and there isn't a corresponding DoS service.

    Args:
        nhs_entity (NHSEntity): The nhs entity to check for the service
        matching_services (List[DosService]): The matching DoS service to check for the
        service_type (CommissionedServiceType): Various constants for the service type
    """
    if nhs_entity.check_for_service(service_type.NHS_UK_SERVICE_CODE) and not next(
        (True for service in matching_services if service.typeid == service_type.DOS_TYPE_ID),
        False,
    ):
        log_missing_dos_service_for_a_given_type(
            nhs_entity=nhs_entity,
            matching_services=matching_services,
            missing_type=service_type,
            reason=f"No '{service_type.TYPE_NAME}' type service profile",
        )


def check_for_missing_palliative_care_service(nhs_entity: NHSEntity, matching_services: list[DoSService]) -> None:
    """Logs when a Change Event has Palliative Care defined and there isn't a corresponding DoS service.

    Args:
        nhs_entity (NHSEntity): The nhs entity to check for the service
        matching_services (List[DosService]): The matching DoS service to check for the
    """
    if nhs_entity.palliative_care and not next(
        (
            True
            for service in matching_services
            if service.typeid == PALLIATIVE_CARE.DOS_TYPE_ID and len(service.odscode) == MAIN_PHARMACY_ODSCODE_LENGTH
        ),
        False,
    ):
        log_missing_dos_service_for_a_given_type(
            nhs_entity=nhs_entity,
            matching_services=matching_services,
            missing_type=PALLIATIVE_CARE,
            reason="No Active Pharmacy with 5 Character ODSCode",
        )
