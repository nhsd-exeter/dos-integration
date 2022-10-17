from typing import List

from aws_lambda_powertools.logging import Logger

from common.appconfig import AppConfig
from common.constants import (
    DENTIST_ORG_TYPE_ID,
    ORGANISATION_SUB_TYPES_KEY,
    PHARMACY_ORG_TYPE_ID,
    SERVICE_TYPES,
    SERVICE_TYPES_ALIAS_KEY,
    VALID_SERVICE_TYPES_KEY,
)
from common.errors import ValidationException

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


def validate_organisation_type_id(org_type_id: str) -> None:
    """Check if the organisation type id is valid

    Args:
        org_type_id (str): organisation type id
    """
    app_config = AppConfig("service-matcher")
    feature_flags = app_config.get_feature_flags()
    in_accepted_org_types: bool = feature_flags.evaluate(
        name="accepted_org_types", context={"org_type": org_type_id}, default=False
    )
    logger.debug(f"Accepted org types: {in_accepted_org_types}")
    if (
        org_type_id == PHARMACY_ORG_TYPE_ID
        and in_accepted_org_types
        or org_type_id == DENTIST_ORG_TYPE_ID
        and in_accepted_org_types
    ):
        logger.append_keys(service_type_alias=SERVICE_TYPES[org_type_id][SERVICE_TYPES_ALIAS_KEY])
        logger.info(
            f"Org type id: {org_type_id} validated",
            extra={"in_accepted_org_types": in_accepted_org_types},
        )
    else:
        logger.append_keys(in_accepted_org_types=in_accepted_org_types)
        logger.append_keys(app_config=app_config.get_raw_configuration())
        raise ValidationException(f"Unexpected Org Type ID: '{org_type_id}'")


def get_valid_service_types(organisation_type_id: str) -> List[int]:
    """Get the valid service types for the organisation type id

    Args:
        organisation_type_id (str): organisation type id from nhs uk entity

    Returns:
        list[int]: set of valid service types
    """
    return SERVICE_TYPES[organisation_type_id][VALID_SERVICE_TYPES_KEY]
