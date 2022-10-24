from typing import List

from aws_lambda_powertools.logging import Logger

from common.constants import SERVICE_TYPES, VALID_SERVICE_TYPES_KEY

logger = Logger(child=True)


def get_valid_service_types(organisation_type_id: str) -> List[int]:
    """Get the valid service types for the organisation type id

    Args:
        organisation_type_id (str): organisation type id from nhs uk entity

    Returns:
        list[int]: set of valid service types
    """
    return SERVICE_TYPES[organisation_type_id][VALID_SERVICE_TYPES_KEY]
