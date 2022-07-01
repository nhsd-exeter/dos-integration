from typing import Any, Dict

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.validation import validate
from aws_lambda_powertools.utilities.validation.exceptions import SchemaValidationError

from common.change_event_exceptions import ValidationException
from common.constants import ODSCODE_LENGTH_KEY, SERVICE_TYPES
from common.service_type import validate_organisation_keys

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
        raise ValidationException(exception)
    validate_organisation_keys(event.get("OrganisationTypeId"), event.get("OrganisationSubType"))
    check_ods_code_length(event["ODSCode"], SERVICE_TYPES[event["OrganisationTypeId"]][ODSCODE_LENGTH_KEY])
    logger.info("Event has been validated")


def check_ods_code_length(odscode: str, odscode_length: int) -> None:
    """Check ODS code length as expected, exception raise if error
    Note: ods code type is checked by schema validation
    Args:
        odscode (str): odscode of NHS UK service
    """
    logger.debug(f"Checking ODSCode {odscode} length")
    if len(odscode) != odscode_length:
        raise ValidationException(f"ODSCode Wrong Length, '{odscode}' is not length {odscode_length}.")


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
