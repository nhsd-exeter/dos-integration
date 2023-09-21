from re import search

from aws_lambda_powertools.logging import Logger
from psycopg import Connection

from ..reporting import (
    log_generic_change_event_error,
    log_service_with_generic_bank_holiday,
    log_website_is_invalid,
)
from common.dos import DoSService
from common.dos_db_connection import query_dos_db
from common.nhs import NHSEntity

logger = Logger(child=True)


def validate_opening_times(dos_service: DoSService, nhs_entity: NHSEntity) -> bool:
    """Validates the opening times match DoS validation rules.

    Args:
        dos_service (DoSService): DoS service object to validate.
        nhs_entity (NHSEntity): NHS entity object to log if validation warning.

    Returns:
        bool: True if opening times match DoS validation rules, False otherwise.
    """
    if dos_service.any_generic_bankholiday_open_periods():
        log_service_with_generic_bank_holiday(nhs_entity, dos_service)
    if not nhs_entity.all_times_valid():
        logger.warning(
            f"Opening Times for NHS Entity '{nhs_entity.odscode}' "
            "were previously found to be invalid or illogical. Skipping change.",
        )
        return False
    return True


def validate_website(nhs_entity: NHSEntity, nhs_website: str, dos_service: DoSService) -> bool:
    """Validates the website matches DoS validation rules.

    Args:
        nhs_entity (NHSEntity): NHS entity object to log if validation warning.
        nhs_website (str): NHS website to validate.
        dos_service (DoSService): DoS service object to validate.

    Returns:
        bool: True if website matches DoS validation rules, False otherwise.
    """
    if search(r"^(https?:\/\/)?([a-z\d][a-z\d-]*[a-z\d]\.)+[a-z]{2,}(\/.*)?$", nhs_website):
        return True
    log_website_is_invalid(nhs_entity, nhs_website, dos_service)
    return False


def validate_z_code_exists_on_service(
    connection: Connection,
    dos_service: DoSService,
    symptom_group_id: int,
    symptom_discriminator_id: int,
    z_code_alias: str,
) -> bool:
    """Validate if the z code exists on the service in the DoS database.

    Args:
        connection (connection): Connection to the DoS database
        dos_service (DoSService): The dos service to update
        symptom_group_id (int): The symptom group
        symptom_discriminator_id (int): The symptom discriminators
        z_code_alias (str): The z code alias for logging purposes

    Returns:
        bool: True if the Z code exists on service, False if it does not
    """
    cursor = query_dos_db(
        connection=connection,
        query=("SELECT id FROM servicesgsds WHERE serviceid=%(SERVICE_ID)s AND sgid=%(SGID)s AND sdid=%(SDID)s;"),
        query_vars={
            "SERVICE_ID": dos_service.id,
            "SGID": symptom_group_id,
            "SDID": symptom_discriminator_id,
        },
    )
    service_sgsd_rowcount = cursor.rowcount
    cursor.close()

    if service_sgsd_rowcount == 1:
        logger.info(f"{z_code_alias} Service's Z code exists in the DoS database")
        return True

    logger.info(f"{z_code_alias} Service's Z code does not exist in the DoS database")
    return False


def validate_z_code_exists(
    connection: Connection,
    dos_service: DoSService,
    symptom_group_id: int,
    symptom_discriminator_id: int,
    z_code_alias: str,
) -> bool:
    """Validates that the Z code exists in the DoS database.

    Args:
        connection (connection): Connection to the DoS database
        dos_service (DoSService): The dos service to update
        symptom_group_id (int): The symptom group id
        symptom_discriminator_id (int): The symptom discriminator id
        z_code_alias (str): The z code alias for logging purposes

    Returns:
        bool: True if the Z code exists, False if it does not
    """
    cursor = query_dos_db(
        connection=connection,
        query=(
            "SELECT id FROM symptomgroupsymptomdiscriminators "
            "WHERE symptomgroupid=%(SGID)s AND symptomdiscriminatorid=%(SDID)s;"
        ),
        query_vars={"SGID": symptom_group_id, "SDID": symptom_discriminator_id},
    )
    symptom_group_symptom_discriminator_combo_rowcount = cursor.rowcount
    cursor.close()

    if symptom_group_symptom_discriminator_combo_rowcount == 1:
        logger.debug(f"{z_code_alias} Z code exists in the DoS database", z_code_alias=z_code_alias)
        return True

    log_generic_change_event_error(
        f"{z_code_alias} Z code does not exist in the DoS database",
        f"{z_code_alias} Z code does not exist",
        f"symptom_group_symptom_discriminator={bool(symptom_group_symptom_discriminator_combo_rowcount)}",
        dos_service,
    )

    return False
