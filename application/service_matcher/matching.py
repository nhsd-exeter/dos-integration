from aws_lambda_powertools.logging import Logger

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
    logger.debug(f"Getting matching DoS Services for odscode '{nhs_entity.odscode}'.")
    matching_services = get_matching_dos_services(nhs_entity.odscode)
    logger.info(
        f"Found {len(matching_services)} services in DB with matching first 5 chars of ODSCode: {matching_services}",
    )

    return matching_services
