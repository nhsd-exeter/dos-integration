from typing import Dict

from aws_lambda_powertools import Logger
from change_request import (
    ADDRESS_CHANGE_KEY,
    ADDRESS_LINES_KEY,
    OPENING_DATES_KEY,
    OPENING_DAYS_KEY,
    PHONE_CHANGE_KEY,
    POSTCODE_CHANGE_KEY,
    PUBLICNAME_CHANGE_KEY,
    WEBSITE_CHANGE_KEY,
)
from common.dos import DoSService, get_valid_dos_postcode
from common.opening_times import SpecifiedOpeningTime
from nhs import NHSEntity
from reporting import log_invalid_nhsuk_pharmacy_postcode

logger = Logger(child=True)


def get_changes(dos_service: DoSService, nhs_entity: NHSEntity) -> Dict[str, str]:
    """Returns a dict of the changes that are required to get
    the service inline with the given nhs_entity.
    """
    changes = {}
    update_changes(changes, WEBSITE_CHANGE_KEY, dos_service.web, nhs_entity.website)
    update_changes(changes, PHONE_CHANGE_KEY, dos_service.publicphone, nhs_entity.phone)
    update_changes(changes, PUBLICNAME_CHANGE_KEY, dos_service.publicname, nhs_entity.org_name)
    update_changes_with_address(changes, dos_service, nhs_entity)
    update_changes_with_postcode(changes, dos_service, nhs_entity)
    update_changes_with_opening_times(changes, dos_service, nhs_entity)
    return changes


def update_changes(changes: dict, change_key: str, dos_value: str, nhs_uk_value: str) -> None:
    """Adds field to the change request if the field is not equal
    Args:
        changes (dict): Change Request changes
        change_key (str): Key to add to the change request
        dos_value (str): Field from the DoS database for comparision
        nhs_uk_value (str): NHS UK Entity value for comparision

    Returns:
        dict: Change Request changes
    """
    if str(dos_value) != str(nhs_uk_value):
        logger.debug(f"{change_key} is not equal, {dos_value=} != {nhs_uk_value=}")
        changes[change_key] = nhs_uk_value


def update_changes_with_address(changes: dict, dos_service: DoSService, nhs_uk_entity: NHSEntity) -> dict:
    """Adds the address to the change request if the address is not equal

    Args:
        changes (dict): Change Request changes
        change_key (str): Key to add to the change request
        dos_address (str): Address from the DoS database for comparision
        nhs_uk_entity (NHSEntity): NHS UK Entity for comparision

    Returns:
        dict: Change Request changes
    """
    nhs_uk_address_string = "$".join(nhs_uk_entity.address_lines)
    dos_address = dos_service.address

    if dos_address != nhs_uk_address_string:
        logger.debug(f"Address is not equal, {dos_address=} != {nhs_uk_address_string=}")
        changes[ADDRESS_CHANGE_KEY] = {ADDRESS_LINES_KEY: nhs_uk_entity.address_lines}

    return changes


def update_changes_with_opening_times(changes: dict, dos_service: DoSService, nhs_entity: NHSEntity) -> None:
    """Adds the standard opening times and specified opening times to the change request if not equal and
    nhsuk times are valid.

    Args:
        changes (dict): Change Request changes
        dos_service (DoSService): DoS Service for comparision
        nhs_entity (NHSEntity): NHS UK Entity for comparision
    """

    # Skip if invalid times. This check will have already been done and logged out fully in event_processor
    if not nhs_entity.all_times_valid():
        logger.warning(
            f"Opening Times for NHS Entity '{nhs_entity.odscode}' were previously found to be invalid or illogical. "
            "Skipping change."
        )
        return

    # SPECIFIED OPENING TIMES (Comparing a list of SpecifiedOpeningTimes)
    dos_spec_open_dates = dos_service.get_specified_opening_times()
    nhs_spec_open_dates = nhs_entity.specified_opening_times
    compared = SpecifiedOpeningTime.equal_lists(dos_spec_open_dates, nhs_spec_open_dates)
    if not compared:
        logger.debug(
            "Specified opening times not equal", extra={"dos": dos_spec_open_dates, "nhs": nhs_spec_open_dates}
        )
        changes[OPENING_DATES_KEY] = SpecifiedOpeningTime.export_cr_format_list(nhs_spec_open_dates)
    else:
        logger.debug(
            "Specified opening times are equal, so no change",
            extra={"dos": dos_spec_open_dates, "nhs": nhs_spec_open_dates, "compared": compared},
        )

    # STANDARD OPENING TIMES (Comparing single StandardOpeningTimes Objects)
    dos_std_open_dates = dos_service.get_standard_opening_times()
    nhs_std_open_dates = nhs_entity.standard_opening_times
    if dos_std_open_dates != nhs_std_open_dates:
        logger.debug(f"Standard weekly opening times not equal. dos={dos_std_open_dates} nhs={nhs_std_open_dates}")
        changes[OPENING_DAYS_KEY] = nhs_std_open_dates.export_cr_format()


def update_changes_with_postcode(changes: dict, dos_service: DoSService, nhs_entity: NHSEntity) -> None:

    dos_postcode = dos_service.normal_postcode()
    nhs_postcode = nhs_entity.normal_postcode()

    if dos_postcode != nhs_postcode:
        logger.debug(f"Postcode is not equal, {dos_postcode=} != {nhs_postcode=}")

        valid_dos_postcode = get_valid_dos_postcode(nhs_postcode)
        if valid_dos_postcode is None:
            log_invalid_nhsuk_pharmacy_postcode(nhs_entity, dos_service)
            if ADDRESS_CHANGE_KEY in changes:
                del changes[ADDRESS_CHANGE_KEY]
                logger.info("Deleted address change as postcode is invalid")
        else:
            changes[ADDRESS_CHANGE_KEY][POSTCODE_CHANGE_KEY] = valid_dos_postcode
