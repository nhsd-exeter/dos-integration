from ast import literal_eval
from os import getenv

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.utilities import parameters

from common.dos import DoSService, get_matching_dos_services
from common.nhs import NHSEntity

logger = Logger(child=True)


def get_matching_services(nhs_entity: NHSEntity) -> list[DoSService]:
    """Gets the matching DoS services for the given nhs entity.

    Using the nhs entity attributed to this object, it finds the
    matching DoS services from the db and filters the results.

    Args:
        nhs_entity (NHSEntity): The nhs entity to match against.

    Returns:
        list[DoSService]: The list of matching DoS services.
    """
    # Check database for services with same first 5 digits of ODSCode
    logger.info(f"Getting matching DoS Services for odscode '{nhs_entity.odscode}'.")
    pharmacy_first_phase_one_feature_flag = get_pharmacy_first_phase_one_feature_flag()
    matching_services = get_matching_dos_services(nhs_entity.odscode, pharmacy_first_phase_one_feature_flag)
    logger.info(
        f"Found {len(matching_services)} services in DB with "
        f"matching first 5 chars of ODSCode: {matching_services}",
        pharmacy_first_phase_one_feature_flag=pharmacy_first_phase_one_feature_flag,
    )

    return matching_services


def get_pharmacy_first_phase_one_feature_flag() -> bool:
    """Gets the pharmacy first phase one feature flag.

    Returns:
        bool: True if the feature flag is enabled, False otherwise.
    """
    parameter_name: str = getenv("PHARMACY_FIRST_PHASE_ONE_PARAMETER")
    pharmacy_first_phase_one: str = parameters.get_parameter(parameter_name)
    pharmacy_first_phase_one_feature_flag = literal_eval(pharmacy_first_phase_one)
    logger.debug(
        "Got pharmacy first phase one feature flag",
        pharmacy_first_phase_one_feature_flag=pharmacy_first_phase_one_feature_flag,
    )
    return pharmacy_first_phase_one_feature_flag
