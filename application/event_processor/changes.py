from re import search, sub
from typing import Any, Dict
from urllib.parse import urlparse, urlunparse

from aws_lambda_powertools import Logger
from change_request import (
    ADDRESS_CHANGE_KEY,
    ADDRESS_LINES_KEY,
    OPENING_DATES_KEY,
    OPENING_DAYS_KEY,
    PHONE_CHANGE_KEY,
    POSTCODE_CHANGE_KEY,
    WEBSITE_CHANGE_KEY,
)
from common.dos import DoSService, get_valid_dos_postcode
from common.nhs import NHSEntity
from common.opening_times import SpecifiedOpeningTime
from common.utilities import is_val_none_or_empty
from reporting import log_invalid_nhsuk_postcode, log_website_is_invalid

logger = Logger(child=True)


def get_changes(dos_service: DoSService, nhs_entity: NHSEntity) -> Dict[str, str]:
    """Returns a dict of the changes that are required to get
    the service inline with the given nhs_entity.
    """
    changes = {}
    update_changes_with_website(changes, dos_service, nhs_entity)
    update_changes(changes, PHONE_CHANGE_KEY, dos_service.publicphone, nhs_entity.phone)
    update_changes_with_address_and_postcode(changes, dos_service, nhs_entity)
    update_changes_with_opening_times(changes, dos_service, nhs_entity)
    return changes


def update_changes(changes: dict, change_key: str, dos_value: Any, nhs_uk_value: Any) -> None:
    """Adds field to the change request if the field is not equal
    Args:
        changes (dict): Change Request changes
        change_key (str): Key to add to the change request
        dos_value (str|None): Field from the DoS database for comparison
        nhs_uk_value (str|None): NHS UK Entity value for comparison

    Returns:
        dict: Change Request changes
    """
    if str(dos_value) != str(nhs_uk_value) and (
        not is_val_none_or_empty(dos_value) or not is_val_none_or_empty(nhs_uk_value)
    ):
        logger.info(f"{change_key} is not equal, {dos_value=} != {nhs_uk_value=}")
        if nhs_uk_value is None:
            changes[change_key] = ""
        else:
            changes[change_key] = nhs_uk_value
    else:
        logger.debug(f"{change_key} is equal, {dos_value=} == {nhs_uk_value=}")


def __update_changes_with_sp_opening_times(changes: dict, dos_service: DoSService, nhs_entity: NHSEntity) -> None:
    """Removes past specified openings and adds specified openings to changes if they differ between dos_service
    and nhs_entity"""
    dos_spec_open_dates = dos_service.get_specified_opening_times()
    nhs_spec_open_dates = nhs_entity.specified_opening_times
    future_nhs_spec_open_dates = SpecifiedOpeningTime.remove_past_dates(nhs_entity.specified_opening_times)
    if len(nhs_spec_open_dates) != len(future_nhs_spec_open_dates):
        logger.info(
            "Removing Specified opening times that occur in the past",
            extra={"all_nhs": nhs_spec_open_dates, "future_nhs": future_nhs_spec_open_dates},
        )
    compared = SpecifiedOpeningTime.equal_lists(dos_spec_open_dates, future_nhs_spec_open_dates)
    if not compared:
        logger.info(
            "Specified opening times not equal", extra={"dos": dos_spec_open_dates, "nhs": future_nhs_spec_open_dates}
        )
        changes[OPENING_DATES_KEY] = SpecifiedOpeningTime.export_cr_format_list(future_nhs_spec_open_dates)
    else:
        logger.debug(
            "Specified opening times are equal, so no change",
            extra={"dos": dos_spec_open_dates, "nhs": future_nhs_spec_open_dates, "compared": compared},
        )


def __update_changes_with_std_opening_times(changes: dict, dos_service: DoSService, nhs_entity: NHSEntity) -> None:
    """Add week opening times to changes if they differ between dos_service and nhs_entity"""
    dos_std_open_dates = dos_service.get_standard_opening_times()
    nhs_std_open_dates = nhs_entity.standard_opening_times
    if dos_std_open_dates != nhs_std_open_dates:
        logger.info(f"Standard weekly opening times not equal. dos={dos_std_open_dates} nhs={nhs_std_open_dates}")
        changes[OPENING_DAYS_KEY] = nhs_std_open_dates.export_cr_format()


def update_changes_with_opening_times(changes: dict, dos_service: DoSService, nhs_entity: NHSEntity) -> None:
    """Adds the standard opening times and specified opening times to the change request if not equal and
    nhsuk times are valid.

    Args:
        changes (dict): Change Request changes
        dos_service (DoSService): DoS Service for comparison
        nhs_entity (NHSEntity): NHS UK Entity for comparison
    """

    if not nhs_entity.all_times_valid():
        logger.warning(
            f"Opening Times for NHS Entity '{nhs_entity.odscode}' were previously found to be invalid or illogical. "
            "Skipping change."
        )
        return

    __update_changes_with_sp_opening_times(changes, dos_service, nhs_entity)
    __update_changes_with_std_opening_times(changes, dos_service, nhs_entity)


def update_changes_with_address_and_postcode(changes: dict, dos_service: DoSService, nhs_entity: NHSEntity) -> None:
    """Adds the address and postcode to the change request if not equal.

    Args:
        changes (dict): Change Request changes
        dos_service (DoSService): DoS Service for comparison
        nhs_entity (NHSEntity): NHS UK Entity for comparison
    """
    logger.debug(f"Address before title casing: {nhs_entity.address_lines}")
    nhs_entity.address_lines = list(map(format_address, nhs_entity.address_lines))
    logger.debug(f"Address after title casing: {nhs_entity.address_lines}")
    nhs_uk_address_string = "$".join(nhs_entity.address_lines)
    dos_address = dos_service.address
    is_address_same = True
    if dos_address != nhs_uk_address_string:
        is_address_same = False
        logger.info(f"Address is not equal, {dos_address=} != {nhs_uk_address_string=}")
        changes[ADDRESS_CHANGE_KEY] = {ADDRESS_LINES_KEY: nhs_entity.address_lines}
    else:
        logger.debug(f"Address is equal, {dos_address=} == {nhs_uk_address_string=}")

    dos_postcode = dos_service.normal_postcode()
    nhs_postcode = nhs_entity.normal_postcode()
    if dos_postcode != nhs_postcode:
        logger.info(f"Postcode is not equal, {dos_postcode=} != {nhs_postcode=}")

        valid_dos_postcode = get_valid_dos_postcode(nhs_postcode)
        if valid_dos_postcode is None:
            log_invalid_nhsuk_postcode(nhs_entity, dos_service)
            if ADDRESS_CHANGE_KEY in changes:
                del changes[ADDRESS_CHANGE_KEY]
                logger.info("Deleted address change as postcode is invalid")
        else:
            if is_address_same:
                changes[ADDRESS_CHANGE_KEY] = {ADDRESS_LINES_KEY: nhs_entity.address_lines}
                logger.debug(f"Address is equal but Postcode is not equal, {dos_postcode=} != {nhs_postcode=}")
            changes[ADDRESS_CHANGE_KEY][POSTCODE_CHANGE_KEY] = valid_dos_postcode
    else:
        logger.debug(f"Postcode are equal, {dos_postcode=} == {nhs_postcode=}")


def format_address(value: str) -> str:
    """Formats an address line to title case and removes apostrophes. As well it replaces any & symbols with and.

    Args:
        value (str): Address line to format
    """
    address = sub(r"[A-Za-z]+('[A-Za-z]+)?", lambda word: word.group(0).capitalize(), value)
    address = address.replace("'", "")
    address = address.replace("&", "and")
    return address


def update_changes_with_website(changes: dict, dos_service: DoSService, nhs_entity: NHSEntity) -> None:
    """Adds the website to the change request if not equal.

    Args:
        changes (dict): Change Request changes
        dos_service (DoSService): DoS Service for comparison
        nhs_entity (NHSEntity): NHS UK Entity for comparison
    """
    if is_val_none_or_empty(nhs_entity.website) and not is_val_none_or_empty(dos_service.web):
        changes[WEBSITE_CHANGE_KEY] = ""
    elif nhs_entity.website is not None and nhs_entity.website != "":
        nhs_uk_website = urlparse(nhs_entity.website)
        if nhs_uk_website.netloc == "":  # handle website like www.test.com
            if "/" in nhs_entity.website:
                nhs_uk_website = nhs_entity.website.split("/")
                nhs_uk_website[0] = nhs_uk_website[0].lower()
                nhs_uk_website = "/".join(nhs_uk_website)
            else:
                nhs_uk_website = urlunparse(nhs_uk_website).lower()
            compare_website(changes, dos_service, nhs_entity, nhs_uk_website)
        else:  # handle website like https://www.test.com
            nhs_uk_website = nhs_uk_website._replace(netloc=nhs_uk_website.netloc.lower())
            nhs_uk_website = urlunparse(nhs_uk_website)
            compare_website(changes, dos_service, nhs_entity, nhs_uk_website)


def compare_website(changes: dict, dos_service: DoSService, nhs_entity: NHSEntity, nhs_website: str) -> None:
    dos_website = dos_service.web
    if dos_website != nhs_website:
        logger.info(f"Website is not equal, {dos_website=} != {nhs_website=}")
        # Regular expression to match DoS's websites check
        # Find on DoS at the directory below
        # pd-api/module/ChangeRequest/src/ChangeRequest/V1/Rest/ChangeRequest/Service/Translate/RequestValidator.php
        if search(r"^(https?:\/\/)?([a-z\d][a-z\d-]*[a-z\d]\.)+[a-z]{2,}(\/.*)?$", nhs_website):
            changes[WEBSITE_CHANGE_KEY] = nhs_website
        else:
            log_website_is_invalid(nhs_entity, nhs_website)
    else:
        logger.debug(f"Website is equal, {dos_website=} == {nhs_website=}")
