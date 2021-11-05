from logging import getLogger
from typing import Any, Dict

from aws_lambda_powertools.utilities.validation import validate
from aws_lambda_powertools.utilities.validation.exceptions import SchemaValidationError


logger = getLogger("lambda")


def validate_event(event: Dict[str, Any]) -> bool:
    """Validate event using business rules

    Args:
        event (Dict[str, Any]): Lambda function invocation event

    Returns:
        bool: True if event is valid, False otherwise
    """
    is_valid_event = True
    try:
        validate(event=event, schema=INPUT_SCHEMA)
    except SchemaValidationError:
        logger.exception(f"Input schema validation error|{event.__str__}")
        return False

    if check_organisation_type(organisation_type=event["OrganisationType"]) is False:
        is_valid_event = False
    if check_ods_code_type_and_length(odscode=event["ODSCode"]) is False:
        is_valid_event = False
    logger.info("event has been validated")
    return is_valid_event


def check_organisation_type(organisation_type: str) -> bool:
    """Check organisation type if matches pharmacy

    Args:
        organisation_type (str): organisation type of NHS UK service

    Returns:
        bool: True is passes validation, False otherwise
    """
    logger.debug("Checking service type")
    if organisation_type == "Pharmacy":
        logger.info(f"Organisation Type {organisation_type}")
        valid = True
    else:
        logger.error(f"Organisation Type not in expected types: {organisation_type}")
        valid = False
    return valid


def check_ods_code_type_and_length(odscode: str) -> bool:
    """Check ODS code type and length as expected

    Args:
        odscode (str): odscode of NHS UK service

    Returns:
        bool: True is passes validation, False otherwise
    """
    logger.debug("Checking ODS code type and length")
    valid = True
    if isinstance(odscode, str) is False:
        logger.error(f"ODS code is not a string: {odscode}")
        valid = False
    if len(odscode) != 5:
        logger.error(f"ODSCode '{odscode}' is not expected length {len(odscode)}")
        valid = False
    return valid


INPUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "http://example.com/example.json",
    "type": "object",
    "title": "The root schema",
    "description": "The root schema comprises the entire JSON document.",
    "default": {},
    "required": [
        "ODSCode",
        "OrganisationType",
    ],
    "properties": {
        "ODSCode": {
            "$id": "#/properties/ODSCode",
            "type": "string",
        },
        "OrganisationType": {
            "$id": "#/properties/OrganisationType",
            "type": "string",
        },
    },
    "additionalProperties": "true",
}
