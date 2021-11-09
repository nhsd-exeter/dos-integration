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
    check_service_type(service_type=event["ServiceType"])
    check_service_sub_type(service_sub_type=event["ServiceSubType"])
    check_ods_code_length(odscode=event["ODSCode"])
    logger.info("Event has been validated")
    return True


def check_service_type(service_type: str) -> None:
    """Check ServiceType if matches PHA, exception raise if error

    Args:
        service_type (str): service type of NHS UK service
    """
    logger.debug("Checking Service Type")
    if service_type == "PHA":
        logger.info(f"Checking Service Type: {service_type}")
    else:
        logger.error(f"Checking Service Type not in expected types: {service_type}")
        raise ValidationException("Unexpected Service Type")


def check_service_sub_type(service_sub_type: str) -> None:
    """Check Service Sub Type if matches COMPH, exception raise if error

    Args:
        service_sub_type (str): service sub type of NHS UK service
    """
    logger.debug("Service Sub Type")
    if service_sub_type == "COMPH":
        logger.info(f"Service Sub Type: {service_sub_type}")
    else:
        logger.error(f"Service Sub Type not in expected types: {service_sub_type}")
        raise ValidationException("Unexpected Service Sub Type")


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
    "$schema": "https://json-schema.org/draft-07/schema",
    "type": "object",
    "required": ["ODSCode", "ServiceType", "ServiceSubType"],
    "properties": {
        "ODSCode": {
            "$id": "#/properties/ODSCode",
            "type": "string",
        },
        "ServiceType": {
            "$id": "#/properties/ServiceType",
            "type": "string",
        },
        "ServiceSubType": {
            "$id": "#/properties/ServiceSubType",
            "type": "string",
        },
    },
    "additionalProperties": "true",
}
