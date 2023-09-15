from aws_lambda_powertools.logging import Logger

from ..reporting import log_invalid_nhsuk_postcode
from .changes_to_dos import ChangesToDoS
from .formatting import format_address, format_website
from .validation import validate_website, validate_z_code_exists
from common.constants import (
    DOS_BLOOD_PRESSURE_SYMPTOM_DISCRIMINATOR,
    DOS_BLOOD_PRESSURE_SYMPTOM_GROUP,
    DOS_CONTRACEPTION_SYMPTOM_DISCRIMINATOR,
    DOS_CONTRACEPTION_SYMPTOM_GROUP,
)
from common.dos import get_valid_dos_location
from common.dos_db_connection import connect_to_dos_db
from common.dos_location import DoSLocation
from common.opening_times import (
    SpecifiedOpeningTime,
    StandardOpeningTimes,
    opening_period_times_from_list,
)
from common.utilities import add_metric, is_val_none_or_empty

logger = Logger(child=True)


def compare_website(changes: ChangesToDoS) -> bool:
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


def compare_public_phone(changes: ChangesToDoS) -> bool:
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


def compare_location(changes: ChangesToDoS) -> tuple[bool, bool, DoSLocation | None]:
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


def compare_standard_opening_times(changes: ChangesToDoS, weekday: str) -> bool:
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


def compare_specified_opening_times(changes: ChangesToDoS) -> bool:
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


def compare_palliative_care(changes: ChangesToDoS) -> bool:
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


def compare_blood_pressure(changes: ChangesToDoS) -> bool:
    """Compares the blood pressure of from the dos_service and nhs_entity.

    Returns:
        bool: True if the blood pressure is different, False if not
    """
    changes.current_blood_pressure = changes.dos_service.blood_pressure
    changes.new_blood_pressure = changes.nhs_entity.blood_pressure
    with connect_to_dos_db() as connection:
        if not validate_z_code_exists(
            connection=connection,
            dos_service=changes.dos_service,
            symptom_group_id=DOS_BLOOD_PRESSURE_SYMPTOM_GROUP,
            symptom_discriminator_id=DOS_BLOOD_PRESSURE_SYMPTOM_DISCRIMINATOR,
            z_code_alias="Blood Pressure",
        ):
            add_metric("DoSBloodPressureZCodeDoesNotExist")

    if changes.current_blood_pressure != changes.new_blood_pressure:
        logger.info(
            f"Blood Pressure is not equal, DoS='{changes.current_blood_pressure}' != NHS UK='{changes.new_blood_pressure}'",  # noqa: E501
            extra={
                "dos_blood_pressure": changes.current_blood_pressure,
                "nhsuk_blood_pressure": changes.new_blood_pressure,
            },
        )
        return True
    logger.info(
        f"Blood Pressure is equal, DoS='{changes.current_blood_pressure}' == NHSUK='{changes.new_blood_pressure}'",
    )
    return False


def compare_contraception(changes: ChangesToDoS) -> bool:
    """Compares the blood pressure of from the dos_service and nhs_entity.

    Returns:
        bool: True if the blood pressure is different, False if not
    """
    changes.current_contraception = changes.dos_service.contraception
    changes.new_contraception = changes.nhs_entity.contraception

    with connect_to_dos_db() as connection:
        if not validate_z_code_exists(
            connection=connection,
            dos_service=changes.dos_service,
            symptom_group_id=DOS_CONTRACEPTION_SYMPTOM_GROUP,
            symptom_discriminator_id=DOS_CONTRACEPTION_SYMPTOM_DISCRIMINATOR,
            z_code_alias="Contraception",
        ):
            add_metric("DoSContraceptionZCodeDoesNotExist")

    if changes.current_contraception != changes.new_contraception:
        logger.info(
            f"Contraception is not equal, DoS='{changes.current_contraception}' != NHS UK='{changes.new_contraception}'",  # noqa: E501
            extra={
                "dos_contraception": changes.current_contraception,
                "nhsuk_contraception": changes.new_contraception,
            },
        )
        return True
    logger.info(
        f"Contraception is equal, DoS='{changes.current_contraception}' == NHSUK='{changes.new_contraception}'",
    )
    return False
