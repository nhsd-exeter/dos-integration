from typing import List
from aws_lambda_powertools import Logger
from common.change_event_exceptions import ValidationException
from common.constants import ORGANISATION_SUB_TYPES_KEY, SERVICE_TYPES, SERVICE_TYPES_NAME_KEY, VALID_SERVICE_TYPES_KEY

logger = Logger(child=True)


def validate_organisation_keys(org_type_id: str, org_sub_type: str) -> None:
    """Validate the organisation type id and organisation sub type

    Args:
        org_type_id (str): organisation type id
        org_sub_type (str): organisation sub type

    Raises:
        ValidationException: Either Org Type ID or Org Sub Type is not part of the valid list
    """
    if org_type_id in SERVICE_TYPES:
        logger.append_keys(service_type=SERVICE_TYPES[org_type_id][SERVICE_TYPES_NAME_KEY])
        logger.info(f"Org type id: {org_type_id} validated")
        logger.info(f"real: {org_sub_type} expected: {SERVICE_TYPES[org_type_id][ORGANISATION_SUB_TYPES_KEY]}")
        if org_sub_type in SERVICE_TYPES[org_type_id][ORGANISATION_SUB_TYPES_KEY]:
            logger.info(f"Subtype type id: {org_sub_type} validated")
        else:
            raise ValidationException(f"Unexpected Org Sub Type ID: '{org_sub_type}'")
    else:
        raise ValidationException(f"Unexpected Org Type ID: '{org_type_id}'")


def get_valid_service_types(organisation_type_id: str) -> List[int]:
    """Get the valid service types for the organisation type id

    Args:
        organisation_type_id (str): organisation type id from nhs uk entity

    Returns:
        list[int]: set of valid service types
    """
    return SERVICE_TYPES[organisation_type_id][VALID_SERVICE_TYPES_KEY]
