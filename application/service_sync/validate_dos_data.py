from aws_lambda_powertools.logging import Logger
from psycopg import Connection

from .reporting import log_generic_change_event_error
from common.dos import DoSService
from common.dos_db_connection import query_dos_db

logger = Logger(child=True)


def validate_dos_z_code_exists(
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
