from typing import Any, Dict

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.validation import validate
from aws_lambda_powertools.utilities.validation.exceptions import SchemaValidationError

from change_event_exceptions import ValidationException

logger = Logger(child=True)


def validate_event(event: Dict[str, Any]) -> None:
    """Validate event using business rules
    Args:
        event (Dict[str, Any]): Lambda function invocation event
    """
    logger.info(f"Attempting to validate event payload: {event}")
    try:
        validate(event=event, schema=INPUT_SCHEMA)
    except SchemaValidationError as exception:
        logger.exception(f"Input schema validation error|{str(exception)}")
        raise ValidationException("Change Event malformed, validation failed")
    check_org_type_id(org_type_id=event["OrganisationTypeId"])
    check_org_sub_type(org_sub_type=event["OrganisationSubType"])
    check_ods_code_length(odscode=event["ODSCode"])
    logger.info("Event has been validated")


def check_org_type_id(org_type_id: str) -> None:
    """Check Organisation Type ID if matches PHA, exception raise if error
    Args:
        org_type_id (str): org type id of NHS UK service
    """
    logger.debug("Checking Organisation Type")
    if org_type_id == "PHA":
        logger.info(f"Org type id: {org_type_id} validated")
    else:
        logger.error(f"Checking Org Type ID not in expected types: {org_type_id}")
        raise ValidationException("Unexpected Org Type ID")


def check_org_sub_type(org_sub_type: str) -> None:
    """Check Organisation Sub Type if matches 'Community', exception raise if error
    Args:
        org_sub_type (str): Organisation sub type of NHS UK service
    """
    logger.debug("Organisation Sub Type")
    if org_sub_type.upper() == "COMMUNITY":
        logger.info(f"Organisation Sub Type: {org_sub_type} validated")
    else:
        logger.error(f"Organisation Sub Type not in expected types: {org_sub_type}")
        raise ValidationException("Unexpected Org Sub Type")


def check_ods_code_length(odscode: str) -> None:
    """Check ODS code length as expected, exception raise if error
    Note: ods code type is checked by schema validation
    Args:
        odscode (str): odscode of NHS UK service
    """
    expected_length = 5
    logger.debug("Checking ODS code type and length")
    if len(odscode) != expected_length:
        logger.error(f"ODSCode '{odscode}' is length {len(odscode)}, not the expected of {expected_length}")
        raise ValidationException("ODSCode Wrong Length")


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
