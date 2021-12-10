from logging import getLogger
from typing import Dict

from change_request import (
    ADDRESS_CHANGE_KEY,
    OPENING_DATES_KEY,
    OPENING_DAYS_KEY,
    PHONE_CHANGE_KEY,
    POSTCODE_CHANGE_KEY,
    PUBLICNAME_CHANGE_KEY,
    WEBSITE_CHANGE_KEY,
)
from dos import DoSService
from nhs import NHSEntity
from opening_times import spec_open_times_cr_format, spec_open_times_equal

logger = getLogger("lambda")


def get_changes(dos_service: DoSService, nhs_entity: NHSEntity) -> Dict[str, str]:
    """Returns a dict of the changes that are required to get
    the service inline with the given nhs_entity.
    """
    changes = {}
    update_changes(changes, WEBSITE_CHANGE_KEY, dos_service.web, nhs_entity.Website)
    update_changes(changes, POSTCODE_CHANGE_KEY, dos_service.postcode, nhs_entity.Postcode)
    update_changes(changes, PHONE_CHANGE_KEY, dos_service.publicphone, nhs_entity.Phone)
    update_changes(changes, PUBLICNAME_CHANGE_KEY, dos_service.publicname, nhs_entity.OrganisationName)
    update_changes_with_address(changes, ADDRESS_CHANGE_KEY, dos_service.address, nhs_entity)
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


def update_changes_with_address(changes: dict, change_key: str, dos_address: str, nhs_uk_entity: NHSEntity) -> dict:
    """Adds the address to the change request if the address is not equal

    Args:
        changes (dict): Change Request changes
        change_key (str): Key to add to the change request
        dos_address (str): Address from the DoS database for comparision
        nhs_uk_entity (NHSEntity): NHS UK Entity for comparision

    Returns:
        dict: Change Request changes
    """
    nhs_uk_address_lines = [
        nhs_uk_entity.Address1,
        nhs_uk_entity.Address2,
        nhs_uk_entity.Address3,
        nhs_uk_entity.City,
        nhs_uk_entity.County,
    ]

    nhs_uk_address = [address for address in nhs_uk_address_lines if address is not None and address.strip() != ""]

    nhs_uk_address_string = "$".join(nhs_uk_address)

    if dos_address != nhs_uk_address_string:
        logger.debug(f"Address is not equal, {dos_address=} != {nhs_uk_address_string=}")
        changes[change_key] = nhs_uk_address

    return changes


def update_changes_with_opening_times(changes: dict, dos_service: DoSService, nhs_entity: NHSEntity) -> None:
    """Adds the standard opening times and specified opening times to the change request if not equal

    Args:
        changes (dict): Change Request changes
        dos_service (DoSService): DoS Service for comparision
        nhs_entity (NHSEntity): NHS UK Entity for comparision
    """
    # SPECIFIED OPENING TIMES (Comparing a list of SpecifiedOpeningTimes)
    dos_spec_open_dates = dos_service.get_specified_opening_times()
    nhs_spec_open_dates = nhs_entity.get_specified_opening_times()
    if not spec_open_times_equal(dos_spec_open_dates, nhs_spec_open_dates):
        logger.debug(f"Specified opening times not equal. dos={dos_spec_open_dates} and nhs={nhs_spec_open_dates}")
        changes[OPENING_DATES_KEY] = spec_open_times_cr_format(nhs_spec_open_dates)

    # STANDARD OPENING TIMES (Comparing single StandardOpeningTimes Objects)
    dos_std_open_dates = dos_service.get_standard_opening_times()
    nhs_std_open_dates = nhs_entity.get_standard_opening_times()
    if dos_std_open_dates != nhs_std_open_dates:
        logger.debug(f"Standard weekly opening times not equal. dos={dos_std_open_dates} and nhs={nhs_std_open_dates}")
        changes[OPENING_DAYS_KEY] = nhs_std_open_dates.export_cr_format()
