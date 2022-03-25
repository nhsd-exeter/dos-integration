from typing import Any, Dict

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.validation import validate
from aws_lambda_powertools.utilities.validation.exceptions import SchemaValidationError

from common.change_event_exceptions import ValidationException
from common.constants import PHARMACY_SERVICE_KEY
from common.service_type import ServiceType

logger = Logger(child=True)

ODSCODE_LENGTH = 5


def validate_event(event: Dict[str, Any]) -> None:
    """Validate event using business rules
    Args:
        event (Dict[str, Any]): Lambda function invocation event
    """
    logger.info(f"Attempting to validate event payload: {event}")
    try:
        validate(event=event, schema=INPUT_SCHEMA)
    except SchemaValidationError as exception:
        raise ValidationException(exception)
    service_type = ServiceType(org_type_id=event["OrganisationTypeId"])
    check_org_sub_type(org_sub_type=event["OrganisationSubType"], service_type=service_type)
    if service_type.name == PHARMACY_SERVICE_KEY:  # Temporary flag to be removed in DI-354
        check_ods_code_length(odscode=event["ODSCode"])
    logger.info("Event has been validated")
    return service_type


def check_org_sub_type(org_sub_type: str, service_type: ServiceType) -> None:
    """Check Organisation Sub Type if matches 'Community', exception raise if error
    Args:
        org_sub_type (str): Organisation sub type of NHS UK service
        service_type (ServiceType): Service Type class object
    """
    logger.debug("Checking Organisation Sub Type")
    if org_sub_type.upper() in service_type.organisation_sub_type:
        logger.info(f"Organisation Sub Type: {org_sub_type} validated")
    else:
        raise ValidationException(
            f"Unexpected Org Sub Type '{org_sub_type}', not part of {service_type.organisation_sub_type}"
        )


def check_ods_code_length(odscode: str) -> None:
    """Check ODS code length as expected, exception raise if error
    Note: ods code type is checked by schema validation
    Args:
        odscode (str): odscode of NHS UK service
    """
    logger.debug("Checking ODS code length")
    if len(odscode) != ODSCODE_LENGTH:
        raise ValidationException(f"ODSCode Wrong Length, '{odscode}' is not length {ODSCODE_LENGTH}.")


INPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft-07/schema",
    "type": "object",
    "required": ["ODSCode", "OrganisationTypeId", "OrganisationSubType"],
    "properties": {
        "ODSCode": {
            "$id": "#/properties/ODSCode",
            "type": "string",
        },
        "OrganisationTypeId": {
            "$id": "#/properties/OrganisationTypeId",
            "type": "string",
        },
        "OrganisationSubType": {
            "$id": "#/properties/OrganisationSubType",
            "type": "string",
        },
    },
    "additionalProperties": "true",
}
