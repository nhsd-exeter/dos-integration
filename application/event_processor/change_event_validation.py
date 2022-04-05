from typing import Any, Dict

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.validation import validate
from aws_lambda_powertools.utilities.validation.exceptions import SchemaValidationError

from common.change_event_exceptions import ValidationException
from common.constants import SERVICE_TYPES, SERVICE_TYPES_NAME_KEY, PHARMACY_SERVICE_KEY
from common.service_type import validate_organisation_keys

logger = Logger(child=True)

PHARMACY_ODSCODE_LENGTH = 5
# DENTIST_ODSCODE_LENGTH = 6


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
    validate_organisation_keys(event.get("OrganisationTypeId"), event.get("OrganisationSubType"))
    if SERVICE_TYPES[event["OrganisationTypeId"]][SERVICE_TYPES_NAME_KEY] == PHARMACY_SERVICE_KEY:
        check_ods_code_length(event["ODSCode"])
    logger.info("Event has been validated")


def check_ods_code_length(odscode: str) -> None:
    """Check ODS code length as expected, exception raise if error
    Note: ods code type is checked by schema validation
    Args:
        odscode (str): odscode of NHS UK service
    """
    logger.debug("Checking ODS code length")
    if len(odscode) != PHARMACY_ODSCODE_LENGTH:
        raise ValidationException(f"ODSCode Wrong Length, '{odscode}' is not length {PHARMACY_ODSCODE_LENGTH}.")


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
