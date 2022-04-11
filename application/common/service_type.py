from os import getenv
from typing import List

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.feature_flags.appconfig import AppConfigStore
from aws_lambda_powertools.utilities.feature_flags.feature_flags import FeatureFlags
from common.change_event_exceptions import ValidationException
from common.constants import (
    DENTIST_ORG_TYPE_ID,
    ORGANISATION_SUB_TYPES_KEY,
    PHARMACY_SERVICE_KEY,
    SERVICE_TYPES,
    SERVICE_TYPES_NAME_KEY,
    VALID_SERVICE_TYPES_KEY,
)

ENVIRONMENT: str = getenv("ENV")
app_config = AppConfigStore(
    environment=ENVIRONMENT,
    application=f"uec-dos-int-{ENVIRONMENT}-lambda-app-config",
    name="event-processor",
)
feature_flags = FeatureFlags(store=app_config)
logger = Logger(child=True)


def validate_organisation_keys(org_type_id: str, org_sub_type: str) -> None:
    """Validate the organisation type id and organisation sub type

    Args:
        org_type_id (str): organisation type id
        org_sub_type (str): organisation sub type

    Raises:
        ValidationException: Either Org Type ID or Org Sub Type is not part of the valid list
    """
    validate_organisation_type_id(org_type_id)
    if org_sub_type in SERVICE_TYPES[org_type_id][ORGANISATION_SUB_TYPES_KEY]:
        logger.info(f"Subtype type id: {org_sub_type} validated")
    else:
        raise ValidationException(f"Unexpected Org Sub Type ID: '{org_sub_type}'")


def validate_organisation_type_id(org_type_id: str) -> bool:
    """Check if the organisation type id is valid

    Args:
        org_type_id (str): organisation type id

    Returns:
        bool: True if valid, False otherwise
    """
    is_pharmacy_accepted: bool = feature_flags.evaluate(name="is_pharmacy_accepted", default=False)
    is_dentist_accepted: bool = feature_flags.evaluate(name="is_dentist_accepted", default=False)
    logger.debug(f"Pharmacy organisation type accepted: {is_pharmacy_accepted}")
    logger.debug(f"Dentist organisation type accepted: {is_dentist_accepted}")
    response = False
    if (
        org_type_id == PHARMACY_SERVICE_KEY
        and is_pharmacy_accepted
        or org_type_id == DENTIST_ORG_TYPE_ID
        and is_dentist_accepted
    ):
        logger.append_keys(service_type=SERVICE_TYPES[org_type_id][SERVICE_TYPES_NAME_KEY])
        logger.info(f"Org type id: {org_type_id} validated")
    else:
        raise ValidationException(
            f"Unexpected Org Type ID: '{org_type_id}'",
            extra={"is_pharmacy_accepted": is_pharmacy_accepted, "is_dentist_accepted": is_dentist_accepted},
        )
    return response


def get_valid_service_types(organisation_type_id: str) -> List[int]:
    """Get the valid service types for the organisation type id

    Args:
        organisation_type_id (str): organisation type id from nhs uk entity

    Returns:
        list[int]: set of valid service types
    """
    return SERVICE_TYPES[organisation_type_id][VALID_SERVICE_TYPES_KEY]
