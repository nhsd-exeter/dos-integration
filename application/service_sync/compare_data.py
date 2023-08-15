from typing import Any

from aws_lambda_powertools.logging import Logger

from .changes_to_dos import ChangesToDoS
from .format import format_address, format_website
from .reporting import (
    log_blank_standard_opening_times,
    log_incorrect_palliative_stockholder_type,
    log_invalid_nhsuk_postcode,
)
from .service_histories import ServiceHistories
from .service_histories_change import ServiceHistoriesChange
from .validation import validate_opening_times, validate_website
from common.constants import (
    DI_LATITUDE_CHANGE_KEY,
    DI_LONGITUDE_CHANGE_KEY,
    DOS_ADDRESS_CHANGE_KEY,
    DOS_EASTING_CHANGE_KEY,
    DOS_NORTHING_CHANGE_KEY,
    DOS_PALLIATIVE_CARE_SGSDID,
    DOS_PALLIATIVE_CARE_TYPE_ID,
    DOS_PHARMACY_NO_PALLIATIVE_CARE_TYPES,
    DOS_POSTAL_TOWN_CHANGE_KEY,
    DOS_POSTCODE_CHANGE_KEY,
    DOS_PUBLIC_PHONE_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_CHANGE_KEY_LIST,
    DOS_WEBSITE_CHANGE_KEY,
    NHS_UK_PALLIATIVE_CARE_SERVICE_CODE,
)
from common.dos import DoSService, get_valid_dos_location
from common.dos_location import DoSLocation
from common.nhs import NHSEntity, get_palliative_care_log_value, skip_if_key_is_none
from common.opening_times import (
    DAY_IDS,
    WEEKDAYS,
    SpecifiedOpeningTime,
    StandardOpeningTimes,
    opening_period_times_from_list,
)
from common.utilities import is_val_none_or_empty

logger = Logger(child=True)


def compare_nhs_uk_and_dos_data(
    dos_service: DoSService,
    nhs_entity: NHSEntity,
    service_histories: ServiceHistories,
) -> ChangesToDoS:
    """Compares the data of the dos_service and nhs_entity and returns a ChangesToDoS object.

    Args:
        dos_service (DoSService): DoSService object to compare
        nhs_entity (NHSEntity): NHS UK entity to compare
        service_histories (ServiceHistories): ServiceHistories object with the service histories of the new changes

    Returns:
        ChangesToDoS: ChangesToDoS class with all the flags if changes need to be made and the changes to make
    """
    # Set up the holder class
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)

    # Compare and validate website
    changes_to_dos = compare_website(changes_to_dos=changes_to_dos)
    # Compare public phone
    changes_to_dos = compare_public_phone(changes_to_dos=changes_to_dos)
    #  Compare and validate address & postcode
    changes_to_dos = compare_location_data(changes_to_dos=changes_to_dos)
    # Compare and validate all opening_times
    changes_to_dos = compare_opening_times(changes_to_dos=changes_to_dos)
    # Compare palliative care
    return compare_palliative_care(changes_to_dos=changes_to_dos)



def has_website_changed(changes: ChangesToDoS) -> bool:
    """Compares the website of from the dos_service and nhs_entity."""
    if is_val_none_or_empty(changes.nhs_entity.website) and not is_val_none_or_empty(changes.dos_service.web):
        # Deleting the existing website
        changes.current_website = changes.dos_service.web
        changes.new_website = None
        return True
    elif changes.nhs_entity.website is not None and changes.nhs_entity.website:  # noqa: RET505
        changes.current_website = changes.dos_service.web
        # Adding a new website
        nhs_uk_website = format_website(changes.nhs_entity.website)
        changes.new_website = nhs_uk_website
        if changes.dos_service.web != nhs_uk_website:
            logger.info(f"Website is not equal, {changes.dos_service.web=} != {nhs_uk_website=}")
            return validate_website(changes.nhs_entity, nhs_uk_website, changes.dos_service)
        logger.info(f"Website is equal, {changes.dos_service.web=} == {nhs_uk_website=}")
    return False


def compare_website(changes_to_dos: ChangesToDoS) -> ChangesToDoS:
    """Compares and creates change for website if needed.

    Args:
        changes_to_dos (ChangesToDoS): ChangesToDoS holder object

    Returns:
        ChangesToDoS: ChangesToDoS holder object
    """
    if has_website_changed(changes=changes_to_dos):
        changes_to_dos = set_up_for_services_table_change(
            changes_to_dos=changes_to_dos,
            change_key=DOS_WEBSITE_CHANGE_KEY,
            new_value=changes_to_dos.new_website,
            previous_value=changes_to_dos.current_website,
            service_table_field_name="web",
        )
    return changes_to_dos


def has_public_phone_changed(changes: ChangesToDoS) -> bool:
    """Compares the public phone of from the dos_service and nhs_entity.

    Returns:
        bool: True if the public phone has changed, False if not
    """
    changes.current_public_phone = changes.dos_service.publicphone
    changes.new_public_phone = changes.nhs_entity.phone
    if str(changes.current_public_phone) != str(changes.new_public_phone) and (
        not is_val_none_or_empty(changes.current_public_phone) or not is_val_none_or_empty(changes.new_public_phone)
    ):
        logger.info(
            f"Public Phone is not equal, DoS='{changes.current_public_phone}' != NHS UK='{changes.new_public_phone}'",
        )
        return True
    logger.info(f"Public Phone is equal, DoS='{changes.current_public_phone}' == NHS UK='{changes.new_public_phone}'")
    return False


def compare_public_phone(changes_to_dos: ChangesToDoS) -> ChangesToDoS:
    """Compares and creates change for publicphone if needed.

    Args:
        changes_to_dos (ChangesToDoS): ChangesToDoS holder object

    Returns:
        ChangesToDoS: ChangesToDoS holder object
    """
    if has_public_phone_changed(changes=changes_to_dos):
        changes_to_dos = set_up_for_services_table_change(
            changes_to_dos=changes_to_dos,
            change_key=DOS_PUBLIC_PHONE_CHANGE_KEY,
            new_value=changes_to_dos.new_public_phone,
            previous_value=changes_to_dos.current_public_phone,
            service_table_field_name="publicphone",
        )
    return changes_to_dos


def has_location_changed(changes: ChangesToDoS) -> tuple[bool, bool, DoSLocation | None]:
    """Check if address and postcode have changed between dos_service and nhs_entity.

    Postcode changes are validated against the DoS locations table.

    Returns:
        Tuple[bool, bool]: Tuple of booleans, first is if address has changed, second is if postcode has changed, third is the DoSLocation object for the postcode
    """  # noqa: E501
    before_title_case_address = changes.nhs_entity.address_lines
    changes.nhs_entity.address_lines = list(map(format_address, changes.nhs_entity.address_lines))
    logger.info(
        f"Address after title casing: {changes.nhs_entity.address_lines}",
        extra={"before": before_title_case_address, "after": changes.nhs_entity.address_lines},
    )
    nhs_uk_address_string = "$".join(changes.nhs_entity.address_lines)
    dos_address = changes.dos_service.address
    is_address_same = True
    if dos_address != nhs_uk_address_string:
        is_address_same = False
        logger.info(f"Address is not equal, {dos_address=} != {nhs_uk_address_string=}")
        changes.new_address = nhs_uk_address_string
        changes.current_address = dos_address
    else:
        logger.info(f"Address is equal, {dos_address=} == {nhs_uk_address_string=}")

    dos_postcode = changes.dos_service.normal_postcode()
    nhs_postcode = changes.nhs_entity.normal_postcode()
    is_postcode_same = True
    valid_dos_location = None
    if dos_postcode != nhs_postcode:
        logger.info(f"Postcode is not equal, {dos_postcode=} != {nhs_postcode=}")
        valid_dos_location = get_valid_dos_location(nhs_postcode)
        valid_dos_postcode = valid_dos_location.postcode if valid_dos_location else None
        if valid_dos_postcode is None:
            log_invalid_nhsuk_postcode(changes.nhs_entity, changes.dos_service)
            if not is_address_same:
                is_address_same = True
                changes.new_address = None
                changes.current_address = None
                logger.info("Deleted address change as postcode is invalid")
        else:
            if is_address_same:
                logger.info(f"Address is equal but Postcode is not equal, {dos_postcode=} != {nhs_postcode=}")
            changes.new_postcode = valid_dos_postcode
            changes.current_postcode = changes.dos_service.postcode
            is_postcode_same = False
    else:
        logger.info(f"Postcode are equal, {dos_postcode=} == {nhs_postcode=}")
    return not is_address_same, not is_postcode_same, valid_dos_location


def compare_location_data(changes_to_dos: ChangesToDoS) -> ChangesToDoS:
    """Compares and creates changes individually for location data items if needed.

    Location data covers the following fields:
        - address
        - postcode
        - latitude
        - longitude
        - town
        - easting
        - northing.

    Args:
        changes_to_dos (ChangesToDoS): ChangesToDoS holder object

    Returns:
        ChangesToDoS: ChangesToDoS holder object
    """
    address_change, postcode_change, dos_location = has_location_changed(changes=changes_to_dos)
    if address_change:
        changes_to_dos = set_up_for_services_table_change(
            changes_to_dos=changes_to_dos,
            change_key=DOS_ADDRESS_CHANGE_KEY,
            new_value=changes_to_dos.new_address,
            previous_value=changes_to_dos.current_address,
            service_table_field_name="address",
        )
    if postcode_change:
        dos_location: DoSLocation  # dos_location can not be none if postcode must be changed
        changes_to_dos = set_up_for_services_table_change(
            changes_to_dos=changes_to_dos,
            change_key=DOS_POSTCODE_CHANGE_KEY,
            new_value=changes_to_dos.new_postcode,
            previous_value=changes_to_dos.current_postcode,
            service_table_field_name="postcode",
        )
        changes_to_dos = set_up_for_services_table_change(
            changes_to_dos=changes_to_dos,
            change_key=DOS_POSTAL_TOWN_CHANGE_KEY,
            new_value=dos_location.postaltown,
            previous_value=changes_to_dos.dos_service.town,
            service_table_field_name="town",
        )
        changes_to_dos = set_up_for_services_table_change(
            changes_to_dos=changes_to_dos,
            change_key=DOS_EASTING_CHANGE_KEY,
            new_value=dos_location.easting,
            previous_value=changes_to_dos.dos_service.easting,
            service_table_field_name="easting",
        )
        changes_to_dos = set_up_for_services_table_change(
            changes_to_dos=changes_to_dos,
            change_key=DOS_NORTHING_CHANGE_KEY,
            new_value=dos_location.northing,
            previous_value=changes_to_dos.dos_service.northing,
            service_table_field_name="northing",
        )
        changes_to_dos = set_up_for_services_table_change(
            changes_to_dos=changes_to_dos,
            change_key=DI_LATITUDE_CHANGE_KEY,
            new_value=dos_location.latitude,
            previous_value=changes_to_dos.dos_service.latitude,
            service_table_field_name="latitude",
            update_service_history=False,
        )
        changes_to_dos = set_up_for_services_table_change(
            changes_to_dos=changes_to_dos,
            change_key=DI_LONGITUDE_CHANGE_KEY,
            new_value=dos_location.longitude,
            previous_value=changes_to_dos.dos_service.longitude,
            service_table_field_name="longitude",
            update_service_history=False,
        )
    return changes_to_dos


def has_standard_opening_times_changed(changes: ChangesToDoS, weekday: str) -> bool:
    """Check if the standard opening times have changed for a specific day.

    Args:
        changes (ChangesToDoS): ChangesToDoS holder object
        weekday (str): The day of the week lowercase to check  (e.g. "monday")

    Returns:
        bool: If there are changes to the standard opening times (not valiated)
    """
    dos_standard_open_dates: StandardOpeningTimes = changes.dos_service.standard_opening_times
    nhs_standard_open_dates: StandardOpeningTimes = changes.nhs_entity.standard_opening_times
    dos_opening_times = dos_standard_open_dates.get_openings(weekday)
    nhs_opening_times = nhs_standard_open_dates.get_openings(weekday.title())
    if not dos_standard_open_dates.same_openings(nhs_standard_open_dates, weekday):
        logger.info(
            f"{weekday.title()} opening times not equal. "
            f"dos={opening_period_times_from_list(dos_opening_times)}, "
            f"nhs={opening_period_times_from_list(nhs_opening_times)}",
        )
        # Set variable for the correct day
        setattr(changes, f"current_{weekday}_opening_times", dos_opening_times)
        setattr(changes, f"new_{weekday}_opening_times", nhs_opening_times)
        return True
    logger.info(
        f"{weekday.title()} opening times are equal, so no change. "
        f"dos={opening_period_times_from_list(dos_opening_times)} "
        f"nhs={opening_period_times_from_list(nhs_opening_times)}",
    )
    return False


def has_specified_opening_times_changed(changes: ChangesToDoS) -> bool:
    """Check if the specified opening times have changed.

    Also past specified opening times are removed from the comparison.

    Returns:
        bool: If there are changes to the specified opening times (not validated)
    """
    dos_spec_open_dates = changes.dos_service.specified_opening_times
    nhs_spec_open_dates = changes.nhs_entity.specified_opening_times
    future_nhs_spec_open_dates = SpecifiedOpeningTime.remove_past_dates(changes.nhs_entity.specified_opening_times)
    if len(nhs_spec_open_dates) != len(future_nhs_spec_open_dates):
        logger.info(
            "Removing Specified opening times that occur in the past",
            extra={"all_nhs": nhs_spec_open_dates, "future_nhs": future_nhs_spec_open_dates},
        )
    if SpecifiedOpeningTime.equal_lists(dos_spec_open_dates, future_nhs_spec_open_dates):
        logger.info(
            "Specified opening times are equal, so no change",
            extra={"dos": dos_spec_open_dates, "nhs": future_nhs_spec_open_dates},
        )
        return False

    logger.info(
        "Specified opening times not equal",
        extra={"dos": dos_spec_open_dates, "nhs": future_nhs_spec_open_dates},
    )
    changes.current_specified_opening_times = dos_spec_open_dates
    changes.new_specified_opening_times = future_nhs_spec_open_dates
    return True


def compare_opening_times(changes_to_dos: ChangesToDoS) -> ChangesToDoS:
    """Compares and creates changes individually for all opening times if needed.

    Args:
        changes_to_dos (ChangesToDoS): ChangesToDoS holder object

    Returns:
        ChangesToDoS: ChangesToDoS holder object
    """
    if changes_to_dos.nhs_entity.standard_opening_times.fully_closed():
        log_blank_standard_opening_times(nhs_entity=changes_to_dos.nhs_entity, dos_service=changes_to_dos.dos_service)
    else:
        logger.debug("Standard opening times are not blank")

    if validate_opening_times(dos_service=changes_to_dos.dos_service, nhs_entity=changes_to_dos.nhs_entity):
        # Compare standard opening times
        logger.info("Opening times are valid")
        for weekday, dos_weekday_key, day_id in zip(WEEKDAYS, DOS_STANDARD_OPENING_TIMES_CHANGE_KEY_LIST, DAY_IDS):  # noqa: B905, E501
            if has_standard_opening_times_changed(changes=changes_to_dos, weekday=weekday):
                changes_to_dos.standard_opening_times_changes[day_id] = getattr(
                    changes_to_dos,
                    f"new_{weekday}_opening_times",
                )
                changes_to_dos.service_histories.add_standard_opening_times_change(
                    current_opening_times=changes_to_dos.dos_service.standard_opening_times,
                    new_opening_times=changes_to_dos.nhs_entity.standard_opening_times,
                    dos_weekday_change_key=dos_weekday_key,
                    weekday=weekday,
                )

        if has_specified_opening_times_changed(changes=changes_to_dos):
            changes_to_dos.specified_opening_times_changes = True
            changes_to_dos.service_histories.add_specified_opening_times_change(
                current_opening_times=changes_to_dos.current_specified_opening_times,
                new_opening_times=changes_to_dos.new_specified_opening_times,
            )
    else:
        logger.info(
            "Opening times are not valid",
            extra={
                "nhs_uk_standard_opening_times": changes_to_dos.nhs_entity.standard_opening_times,
                "nhs_uk_specified_opening_times": changes_to_dos.nhs_entity.specified_opening_times,
            },
        )
    return changes_to_dos


def set_up_for_services_table_change(  # noqa: PLR0913
    changes_to_dos: ChangesToDoS,
    change_key: str,
    new_value: Any,  # noqa: ANN401
    previous_value: Any,  # noqa: ANN401
    service_table_field_name: str,
    update_service_history: bool = True,
) -> ChangesToDoS:
    """Runs the prerequisites for a change to the services table.

    Including adding the change to the change object, and updating the service history.

    Args:
        changes_to_dos (ChangesToDoS): The changes to dos object
        change_key (str): The service history change key
        new_value (Any): The new value to set the service table field to
        previous_value (Any): The previous value of the service table field
        service_table_field_name (str): The name of the service table field to set
        update_service_history (bool): Whether to update the service history. Defaults to True.

    Returns:
        ChangesToDoS: The changes to dos object
    """
    changes_to_dos.demographic_changes[service_table_field_name] = str(new_value) if new_value is not None else ""
    if update_service_history:
        changes_to_dos.service_histories.add_change(
            dos_change_key=change_key,
            change=ServiceHistoriesChange(
                data=new_value,
                previous_value=previous_value,
                change_key=change_key,
            ),
        )
    return changes_to_dos


def has_palliative_care_changed(changes: ChangesToDoS) -> bool:
    """Compares the palliative care of from the dos_service and nhs_entity.

    Returns:
        bool: True if the palliative care is different, False if not
    """
    changes.current_palliative_care = changes.dos_service.palliative_care
    changes.new_palliative_care = changes.nhs_entity.palliative_care
    if changes.current_palliative_care != changes.new_palliative_care:
        logger.info(
            f"Palliative Care is not equal, DoS='{changes.current_palliative_care}' != NHS UK='{changes.new_palliative_care}'",  # noqa: E501
            extra={
                "dos_palliative_care": changes.current_palliative_care,
                "nhsuk_palliative_care": changes.new_palliative_care,
            },
        )
        return True
    logger.info(
        f"Palliative Care is equal, DoS='{changes.current_palliative_care}' == NHSUK='{changes.new_palliative_care}'",  # noqa: E501
    )
    return False


def compare_palliative_care(changes_to_dos: ChangesToDoS) -> ChangesToDoS:
    """Compares palliative care.

    Args:
        changes_to_dos (ChangesToDoS): ChangesToDoS holder object

    Returns:
        ChangesToDoS: ChangesToDoS holder object
    """
    skip_palliative_care_check = skip_if_key_is_none(
        changes_to_dos.nhs_entity.extract_uec_service(NHS_UK_PALLIATIVE_CARE_SERVICE_CODE),
    )
    logger.info(f"Skip palliative care check: {skip_palliative_care_check}")
    if (
        changes_to_dos.dos_service.typeid == DOS_PALLIATIVE_CARE_TYPE_ID
        and has_palliative_care_changed(changes=changes_to_dos)
        and skip_palliative_care_check is False
    ):
        changes_to_dos.palliative_care_changes = True

        changes_to_dos.service_histories.add_sgsdid_change(
            sgsdid=DOS_PALLIATIVE_CARE_SGSDID,
            new_value=changes_to_dos.nhs_entity.palliative_care,
        )
    elif (
        changes_to_dos.dos_service.typeid in DOS_PHARMACY_NO_PALLIATIVE_CARE_TYPES
        and changes_to_dos.dos_service.palliative_care is True
    ):
        nhs_uk_palliative_care = get_palliative_care_log_value(
            changes_to_dos.nhs_entity.palliative_care,
            skip_palliative_care_check,
        )
        log_incorrect_palliative_stockholder_type(
            nhs_uk_palliative_care=nhs_uk_palliative_care,
            dos_palliative_care=changes_to_dos.dos_service.palliative_care,
            dos_service=changes_to_dos.dos_service,
        )
    else:
        logger.info(
            "No change / Not suitable for palliative care comparison",
            extra={
                "nhs_uk_palliative_care": get_palliative_care_log_value(
                    changes_to_dos.nhs_entity.palliative_care,
                    skip_palliative_care_check,
                ),
                "dos_palliative_care": changes_to_dos.dos_service.palliative_care,
            },
        )
    return changes_to_dos
