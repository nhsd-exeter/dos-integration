from logging import getLogger
from typing import Any, Dict

from aws_lambda_powertools.utilities.validation import validate
from aws_lambda_powertools.utilities.validation.exceptions import SchemaValidationError
from change_event_exceptions import ValidationException

logger = getLogger("lambda")


def valid_event(event: Dict[str, Any]) -> bool:
    """Validate event using business rules

    Args:
        event (Dict[str, Any]): Lambda function invocation event

    Returns:
        bool: True if event is valid, otherwise Exception
    """
    try:
        validate(event=event, schema=INPUT_SCHEMA)
    except SchemaValidationError as exception:
        logger.exception(f"Input schema validation error|{str(exception)}")
        return False
    check_organisation_type(organisation_type=event["OrganisationType"])
    check_ods_code_length(odscode=event["ODSCode"])
    logger.info("Event has been validated")
    return True


def check_organisation_type(organisation_type: str) -> None:
    """Check organisation type if matches pharmacy, exception raise if error

    Args:
        organisation_type (str): organisation type of NHS UK service
    """
    logger.debug("Checking service type")
    if organisation_type == "Pharmacy":
        logger.info(f"Organisation Type {organisation_type}")
    else:
        logger.error(f"Organisation Type not in expected types: {organisation_type}")
        raise ValidationException("Unexpected Organisation Type")


def check_ods_code_length(odscode: str) -> None:
    """Check ODS code length as expected, exception raise if error
    Note: ods code type is checked by schema validation

    Args:
        odscode (str): odscode of NHS UK service
    """
    logger.debug("Checking ODS code type and length")
    if len(odscode) != 5:
        logger.error(f"ODSCode '{odscode}' is not expected length {len(odscode)}")
        raise ValidationException("ODSCode Wrong Length")
    logger.debug("Checking ODS code matches expected format")


INPUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
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
