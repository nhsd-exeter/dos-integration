from aws_lambda_powertools.logging import Logger
from psycopg import Connection

from .reporting import log_to_quality_check_report
from .search_dos import (
    search_for_incorrectly_profiled_z_code_on_correct_type,
    search_for_incorrectly_profiled_z_code_on_incorrect_type,
    search_for_matching_services,
    search_for_pharmacy_ods_codes,
)
from common.commissioned_service_type import BLOOD_PRESSURE, CONTRACEPTION, PALLIATIVE_CARE, CommissionedServiceType
from common.dos import DoSService

logger = Logger(child=True)


def check_pharmacy_profiling(connection: Connection) -> None:
    """Check the pharmacy profiling data quality of the dos database.

    Args:
        connection (Connection): Connection to the DoS DB.
    """
    odscodes = search_for_pharmacy_ods_codes(connection)
    for odscode in odscodes:
        logger.append_keys(odscode=odscode)
        logger.info(f"Checking pharmacy profiling for odscode '{odscode}'.")
        matched_services = search_for_matching_services(connection, odscode)
        check_for_multiple_of_service_type(matched_services, BLOOD_PRESSURE)
        check_for_multiple_of_service_type(matched_services, CONTRACEPTION)
        logger.remove_keys("odscode")


def check_for_zcode_profiling_on_incorrect_type(connection: Connection, service_type: CommissionedServiceType) -> None:
    """Check the zcode profiling data quality of the dos database.

    Args:
        connection (Connection): Connection to the DoS DB.
        service_type (CommissionedServiceType): Service type to check for.
    """
    if incorrectly_profiled_services := search_for_incorrectly_profiled_z_code_on_incorrect_type(
        connection,
        service_type,
    ):
        log_to_quality_check_report(
            incorrectly_profiled_services,
            f"{service_type.TYPE_NAME} ZCode is on invalid service type",
            service_type.DOS_SG_SD_ID,
        )


def check_for_palliative_care_profiling(connection: Connection) -> None:
    """Check the zcode profiling data quality of the dos database.

    Args:
        connection (Connection): Connection to the DoS DB.
        service_type (CommissionedServiceType): Service type to check for.
    """
    check_for_zcode_profiling_on_incorrect_type(connection, PALLIATIVE_CARE)
    if incorrectly_profiled_services := search_for_incorrectly_profiled_z_code_on_correct_type(
        connection,
        PALLIATIVE_CARE,
    ):
        logger.info(
            f"Found {len(incorrectly_profiled_services)} incorrectly "
            f"profiled {PALLIATIVE_CARE.TYPE_NAME.lower()} services.",
            services=incorrectly_profiled_services,
        )
        log_to_quality_check_report(
            incorrectly_profiled_services,
            f"{PALLIATIVE_CARE.TYPE_NAME} ZCode is on the correct service type, "
            "but the service is incorrectly profiled",
            PALLIATIVE_CARE.DOS_SG_SD_ID,
        )


def check_for_multiple_of_service_type(
    matched_services: list[DoSService],
    service_type: CommissionedServiceType,
) -> None:
    """Check for multiple of service type.

    Args:
        matched_services (list[DoSService]): List of matched services.
        service_type (CommissionedServiceType): Service type to check for.
    """
    matched_service_types = [service for service in matched_services if service.typeid == service_type.DOS_TYPE_ID]
    if len(matched_service_types) > 1:
        log_to_quality_check_report(
            matched_service_types,
            f"Multiple 'Pharmacy' type services found (type {service_type.DOS_TYPE_ID})",
        )
