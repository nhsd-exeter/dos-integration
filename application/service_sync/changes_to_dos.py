from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from aws_lambda_powertools.logging import Logger

from .dos_logger import DoSLogger
from .format import format_address, format_website
from .service_histories import ServiceHistories
from .service_histories_change import ServiceHistoriesChange
from .validation import validate_opening_times, validate_website
from common.constants import (
    DOS_ADDRESS_CHANGE_KEY,
    DOS_POSTCODE_CHANGE_KEY,
    DOS_PUBLIC_PHONE_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_CHANGE_KEY_LIST,
    DOS_WEBSITE_CHANGE_KEY,
)
from common.dos import DoSService, get_valid_dos_postcode
from common.nhs import NHSEntity
from common.opening_times import (
    DAY_IDS,
    opening_period_times_from_list,
    SpecifiedOpeningTime,
    StandardOpeningTimes,
    WEEKDAYS,
)
from common.report_logging import log_invalid_nhsuk_postcode
from common.utilities import is_val_none_or_empty

logger = Logger(child=True)


@dataclass(init=True, repr=True)
class ChangesToDoS:
    """Class to determine if an update needs to be made to the DoS db and if so, what the update should be"""

    # Holding data classes for use within this class
    dos_service: DoSService
    nhs_entity: NHSEntity
    service_histories: ServiceHistories
    dos_logger: DoSLogger
    # Varible to know if fields need to be changed
    demographic_changes: Dict[Optional[str], Any] = field(default_factory=dict)
    standard_opening_times_changes: Dict[Optional[int], Any] = field(default_factory=dict)
    specified_opening_times_changes: bool = False

    # New value to be saved to the database
    new_address: Optional[str] = None
    new_postcode: Optional[str] = None
    new_public_phone: Optional[str] = None
    new_specified_opening_times: Optional[List[SpecifiedOpeningTime]] = None
    new_website: Optional[str] = None

    # Existing DoS data for use building service history
    current_address: Optional[str] = None
    current_postcode: Optional[str] = None
    current_public_phone: Optional[str] = None
    current_specified_opening_times: Optional[List[SpecifiedOpeningTime]] = None
    current_website: Optional[str] = None

    # Each day that has changed will have a current and new value in the format below
    # new_day_opening_times e.g. new_monday_opening_times
    # current_day_opening_times e.g. current_monday_opening_times
    # The type of the value is a list of OpenPeriod objects

    def check_for_standard_opening_times_day_changes(self, weekday: str) -> bool:
        """Check if the standard opening times have changed for a specific day

        Args:
            weekday (str): The day of the week lowercase to check  (e.g. "monday")

        Returns:
            bool: If there are changes to the standard opening times (not valiated)
        """
        dos_standard_open_dates: StandardOpeningTimes = self.dos_service.standard_opening_times
        nhs_standard_open_dates: StandardOpeningTimes = self.nhs_entity.standard_opening_times
        dos_opening_times = dos_standard_open_dates.get_openings(weekday)
        nhs_opening_times = nhs_standard_open_dates.get_openings(weekday.title())
        if not dos_standard_open_dates.same_openings(nhs_standard_open_dates, weekday):
            logger.info(
                (
                    f"{weekday.title()} opening times not equal. "
                    f"dos={opening_period_times_from_list(dos_opening_times)}, "
                    f"nhs={opening_period_times_from_list(nhs_opening_times)}"
                )
            )
            # Set variable for the correct day
            setattr(self, f"current_{weekday}_opening_times", dos_opening_times)
            setattr(self, f"new_{weekday}_opening_times", nhs_opening_times)
            return True
        else:
            logger.info(
                (
                    f"{weekday.title()} opening times are equal, so no change. "
                    f"dos={opening_period_times_from_list(dos_opening_times)} "
                    f"nhs={opening_period_times_from_list(nhs_opening_times)}"
                )
            )
            return False

    def check_for_specified_opening_times_changes(self) -> bool:
        """Check if the specified opening times have changed
        Also past specified opening times are removed from the comparison

        Returns:
            bool: If there are changes to the specified opening times (not valiated)
        """
        dos_spec_open_dates = self.dos_service.specified_opening_times
        nhs_spec_open_dates = self.nhs_entity.specified_opening_times
        future_nhs_spec_open_dates = SpecifiedOpeningTime.remove_past_dates(self.nhs_entity.specified_opening_times)
        if len(nhs_spec_open_dates) != len(future_nhs_spec_open_dates):
            logger.info(
                "Removing Specified opening times that occur in the past",
                extra={"all_nhs": nhs_spec_open_dates, "future_nhs": future_nhs_spec_open_dates},
            )
        equal_specified_opening_times = SpecifiedOpeningTime.equal_lists(
            dos_spec_open_dates, future_nhs_spec_open_dates
        )
        if not equal_specified_opening_times or len(nhs_spec_open_dates) != len(future_nhs_spec_open_dates):
            logger.info(
                "Specified opening times not equal",
                extra={"dos": dos_spec_open_dates, "nhs": future_nhs_spec_open_dates},
            )
            self.current_specified_opening_times = dos_spec_open_dates
            self.new_specified_opening_times = future_nhs_spec_open_dates
            return True
        else:
            logger.info(
                "Specified opening times are equal, so no change",
                extra={"dos": dos_spec_open_dates, "nhs": future_nhs_spec_open_dates},
            )
            return False

    def check_for_address_and_postcode_for_changes(self) -> Tuple[bool, bool]:
        """Check if address and postcode have changed between dos_service and nhs_entity,
        Postcode changes are validated against the DoS locations table

        Returns:
            Tuple[bool, bool]: Tuple of booleans, first is if address has changed, second is if postcode has changed
        """
        logger.debug(f"Address before title casing: {self.nhs_entity.address_lines}")
        self.nhs_entity.address_lines = list(map(format_address, self.nhs_entity.address_lines))
        logger.debug(f"Address after title casing: {self.nhs_entity.address_lines}")
        nhs_uk_address_string = "$".join(self.nhs_entity.address_lines)
        dos_address = self.dos_service.address
        is_address_same = True
        if dos_address != nhs_uk_address_string:
            is_address_same = False
            logger.info(f"Address is not equal, {dos_address=} != {nhs_uk_address_string=}")
            self.new_address = nhs_uk_address_string
            self.current_address = dos_address
        else:
            logger.info(f"Address is equal, {dos_address=} == {nhs_uk_address_string=}")

        dos_postcode = self.dos_service.normal_postcode()
        nhs_postcode = self.nhs_entity.normal_postcode()
        is_postcode_same = True
        if dos_postcode != nhs_postcode:
            logger.info(f"Postcode is not equal, {dos_postcode=} != {nhs_postcode=}")

            valid_dos_postcode = get_valid_dos_postcode(nhs_postcode)
            if valid_dos_postcode is None:
                log_invalid_nhsuk_postcode(self.nhs_entity, self.dos_service)
                if not is_address_same:
                    is_address_same = True
                    self.new_address = None
                    self.current_address = None
                    logger.info("Deleted address change as postcode is invalid")
            else:
                if is_address_same:
                    logger.info(f"Address is equal but Postcode is not equal, {dos_postcode=} != {nhs_postcode=}")
                self.new_postcode = valid_dos_postcode
                self.current_postcode = self.dos_service.postcode
                is_postcode_same = False
        else:
            logger.info(f"Postcode are equal, {dos_postcode=} == {nhs_postcode=}")
        return not is_address_same, not is_postcode_same

    def check_website_for_change(self) -> bool:
        """Compares the website of from the dos_service and nhs_entity"""
        if is_val_none_or_empty(self.nhs_entity.website) and not is_val_none_or_empty(self.dos_service.web):
            # Deleting the existing website
            self.current_website = self.dos_service.web
            self.new_website = None
            return True
        elif self.nhs_entity.website is not None and self.nhs_entity.website != "":
            self.current_website = self.dos_service.web
            # Adding a new website
            nhs_uk_website = format_website(self.nhs_entity.website)
            self.new_website = nhs_uk_website
            return self.compare_and_validate_website(self.dos_service, self.nhs_entity, nhs_uk_website)
        return False

    def compare_and_validate_website(self, dos_service: DoSService, nhs_entity: NHSEntity, nhs_website: str) -> bool:
        """Compares the website of from the dos_service and formatted nhs website

        Args:
            dos_service (DoSService): DoSService object to compare
            nhs_entity (NHSEntity): NHS Entity object to compare
            nhs_website (str): Formatted NHS website

        Returns:
            bool: True if the website has changed and is valid, False if not
        """
        dos_website = dos_service.web
        if dos_website != nhs_website:
            logger.info(f"Website is not equal, {dos_website=} != {nhs_website=}")
            # Regular expression to match DoS's websites check
            return validate_website(nhs_entity, nhs_website)
        else:
            logger.info(f"Website is equal, {dos_website=} == {nhs_website=}")
        return False

    def check_public_phone_for_change(self) -> bool:
        """Compares the public phone of from the dos_service and nhs_entity

        Returns:
            bool: True if the public phone has changed, False if not
        """
        self.current_public_phone = self.dos_service.publicphone
        self.new_public_phone = self.nhs_entity.phone
        if str(self.current_public_phone) != str(self.new_public_phone) and (
            not is_val_none_or_empty(self.current_public_phone) or not is_val_none_or_empty(self.new_public_phone)
        ):
            logger.info(
                f"Public Phone is not equal, DoS='{self.current_public_phone}' != NHS UK='{self.new_public_phone}'"
            )
            return True
        else:
            logger.debug(
                f"Public Phone is equal, DoS='{self.current_public_phone}' == NHS UK='{self.new_public_phone}'"
            )
            return False


def compare_nhs_uk_and_dos_data(
    dos_service: DoSService, nhs_entity: NHSEntity, service_histories: ServiceHistories
) -> ChangesToDoS:
    """Compares the data of the dos_service and nhs_entity and returns a ChangesToDoS object.

    Args:
        dos_service (DoSService): DoSService object to compare
        nhs_entity (NHSEntity): NHS UK entity to compare
        service_histories (ServiceHistories): ServiceHistories object with the service histories of the new changes

    Returns:
        ChangesToDoS: ChangesToDoS class with all the flags if changes need to be made and the changes to make
    """
    dos_logger = DoSLogger(
        correlation_id=logger.get_correlation_id(),
        service_uid=str(dos_service.uid),
        service_name=dos_service.name,
        type_id=str(dos_service.typeid),
    )
    # Set up the holder class
    changes_to_dos = ChangesToDoS(
        dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories, dos_logger=dos_logger
    )

    # Compare and validate website
    if changes_to_dos.check_website_for_change():
        # Website has changed, is valid, so add to changes
        changes_to_dos.demographic_changes["web"] = changes_to_dos.new_website
        service_history_change = ServiceHistoriesChange(
            data=changes_to_dos.new_website,
            previous_value=changes_to_dos.current_website,
            change_key=DOS_WEBSITE_CHANGE_KEY,
        )
        changes_to_dos.service_histories.add_change(
            dos_change_key=DOS_WEBSITE_CHANGE_KEY,
            change=service_history_change,
        )
        dos_logger.log_service_update(
            data_field_modified=DOS_WEBSITE_CHANGE_KEY,
            action=service_history_change.change_action,
            previous_value=changes_to_dos.current_website,
            new_value=changes_to_dos.new_website,
        )

    # Compare public phone
    if changes_to_dos.check_public_phone_for_change():
        # Website has changed, is valid, so add to changes
        changes_to_dos.demographic_changes["publicphone"] = changes_to_dos.new_public_phone
        changes_to_dos.service_histories.add_change(
            dos_change_key=DOS_PUBLIC_PHONE_CHANGE_KEY,
            change=ServiceHistoriesChange(
                data=changes_to_dos.new_public_phone,
                previous_value=changes_to_dos.current_public_phone,
                change_key=DOS_PUBLIC_PHONE_CHANGE_KEY,
            ),
        )
        dos_logger.log_service_update(
            data_field_modified=DOS_PUBLIC_PHONE_CHANGE_KEY,
            action=service_history_change.change_action,
            previous_value=changes_to_dos.current_public_phone,
            new_value=changes_to_dos.new_public_phone,
        )

    # Compare and validate address & postcode
    address_change, postcode_change = changes_to_dos.check_for_address_and_postcode_for_changes()
    if address_change:
        changes_to_dos.demographic_changes["address"] = changes_to_dos.new_address
        changes_to_dos.service_histories.add_change(
            dos_change_key=DOS_ADDRESS_CHANGE_KEY,
            change=ServiceHistoriesChange(
                data=changes_to_dos.new_address,
                previous_value=changes_to_dos.current_address,
                change_key=DOS_ADDRESS_CHANGE_KEY,
            ),
        )
        dos_logger.log_service_update(
            data_field_modified=DOS_ADDRESS_CHANGE_KEY,
            action=service_history_change.change_action,
            previous_value=changes_to_dos.current_address,
            new_value=changes_to_dos.new_address,
        )
    if postcode_change:
        changes_to_dos.demographic_changes["postcode"] = changes_to_dos.new_postcode
        changes_to_dos.service_histories.add_change(
            dos_change_key=DOS_POSTCODE_CHANGE_KEY,
            change=ServiceHistoriesChange(
                data=changes_to_dos.new_postcode,
                previous_value=changes_to_dos.current_postcode,
                change_key=DOS_POSTCODE_CHANGE_KEY,
            ),
        )
        dos_logger.log_service_update(
            data_field_modified=DOS_POSTCODE_CHANGE_KEY,
            action=service_history_change.change_action,
            previous_value=changes_to_dos.current_postcode,
            new_value=changes_to_dos.new_postcode,
        )

    if validate_opening_times(dos_service=changes_to_dos.dos_service, nhs_entity=changes_to_dos.nhs_entity):
        # Compare standard opening times
        logger.debug("Opening times are valid")
        for weekday, dos_weekday_key, day_id in zip(WEEKDAYS, DOS_STANDARD_OPENING_TIMES_CHANGE_KEY_LIST, DAY_IDS):
            if changes_to_dos.check_for_standard_opening_times_day_changes(weekday=weekday):
                changes_to_dos.standard_opening_times_changes[day_id] = getattr(
                    changes_to_dos, f"new_{weekday}_opening_times"
                )
                change = changes_to_dos.service_histories.add_standard_opening_times_change(
                    current_opening_times=changes_to_dos.dos_service.standard_opening_times,
                    new_opening_times=changes_to_dos.nhs_entity.standard_opening_times,
                    dos_weekday_change_key=dos_weekday_key,
                    weekday=weekday,
                )
                dos_logger.log_standard_opening_times_service_update_for_weekday(
                    data_field_modified=dos_weekday_key,
                    action=change.change_action,
                    previous_value=changes_to_dos.dos_service.standard_opening_times,
                    new_value=changes_to_dos.nhs_entity.standard_opening_times,
                    weekday=weekday,
                )

        if changes_to_dos.check_for_specified_opening_times_changes():
            changes_to_dos.specified_opening_times_changes = True
            change = changes_to_dos.service_histories.add_specified_opening_times_change(
                current_opening_times=changes_to_dos.current_specified_opening_times,
                new_opening_times=changes_to_dos.new_specified_opening_times,
            )
            dos_logger.log_specified_opening_times_service_update(
                action=change.change_action,
                previous_value=changes_to_dos.current_specified_opening_times,
                new_value=changes_to_dos.new_specified_opening_times,
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
