from re import search

from aws_lambda_powertools.logging import Logger

from common.dos import DoSService
from common.nhs import NHSEntity
from common.report_logging import log_service_with_generic_bank_holiday, log_website_is_invalid

logger = Logger(child=True)


def validate_opening_times(dos_service: DoSService, nhs_entity: NHSEntity) -> bool:
    """Validates the opening times match DoS validation rules.

    Args:
        dos_service (DoSService): DoS service object to validate.
        nhs_entity (NHSEntity): NHS entity object to log if validation warning.

    Returns:
        bool: True if opening times match DoS validation rules, False otherwise.
    """
    if dos_service.any_generic_bankholiday_open_periods():
        log_service_with_generic_bank_holiday(nhs_entity, dos_service)
    if not nhs_entity.all_times_valid():
        logger.warning(
            f"Opening Times for NHS Entity '{nhs_entity.odscode}' "
            "were previously found to be invalid or illogical. Skipping change.",
        )
        return False
    return True


def validate_website(nhs_entity: NHSEntity, nhs_website: str) -> bool:
    """Validates the website matches DoS validation rules.

    Args:
        nhs_entity (NHSEntity): NHS entity object to log if validation warning.
        nhs_website (str): NHS website to validate.

    Returns:
        bool: True if website matches DoS validation rules, False otherwise.
    """
    if search(r"^(https?:\/\/)?([a-z\d][a-z\d-]*[a-z\d]\.)+[a-z]{2,}(\/.*)?$", nhs_website):
        return True
    log_website_is_invalid(nhs_entity, nhs_website)
    return False
