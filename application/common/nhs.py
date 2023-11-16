from dataclasses import dataclass
from datetime import datetime
from itertools import groupby
from typing import Self

from aws_lambda_powertools.logging import Logger

from common.constants import (
    CLOSED_AND_HIDDEN_STATUSES,
    NHS_UK_BLOOD_PRESSURE_SERVICE_CODE,
    NHS_UK_CONTRACEPTION_SERVICE_CODE,
    NHS_UK_PALLIATIVE_CARE_SERVICE_CODE,
    PHARMACY_SERVICE_TYPE_IDS,
)
from common.dos import DoSService
from common.opening_times import WEEKDAYS, OpenPeriod, SpecifiedOpeningTime, StandardOpeningTimes

logger = Logger(child=True)


@dataclass
class NHSEntity:
    """This is an object to store an NHS Entity data.

    Some fields are pulled straight from the payload while others are processed first. So attribute
    names differ from payload format for consistency within object.
    """

    entity_data: dict
    odscode: str
    org_name: str
    org_type_id: str
    org_type: str
    org_sub_type: str
    org_status: str
    address_lines: list[str]
    postcode: str
    website: str
    phone: str
    standard_opening_times: StandardOpeningTimes | None
    specified_opening_times: list[SpecifiedOpeningTime] | None
    palliative_care: bool
    blood_pressure: bool
    contraception: bool

    def __init__(self: Self, entity_data: dict) -> None:
        """Initialise the object with the entity data."""
        self.entity_data = entity_data

        self.odscode = entity_data.get("ODSCode")
        self.org_name = entity_data.get("OrganisationName")
        self.org_type_id = entity_data.get("OrganisationTypeId")
        self.org_type = entity_data.get("OrganisationType")
        self.org_sub_type = entity_data.get("OrganisationSubType")
        self.org_status = entity_data.get("OrganisationStatus")
        self.postcode = entity_data.get("Postcode")
        self.parent_org_name = entity_data.get("ParentOrganisation", {}).get("OrganisationName")
        self.address_lines = [
            line
            for line in [entity_data.get(x) for x in [f"Address{i}" for i in range(1, 5)] + ["City", "County"]]
            if isinstance(line, str) and line.strip()
        ]

        self.standard_opening_times = self._get_standard_opening_times()
        self.specified_opening_times = self._get_specified_opening_times()
        self.phone = self.extract_contact("Telephone")
        self.website = self.extract_contact("Website")
        self.palliative_care = self.check_for_uec_service(NHS_UK_PALLIATIVE_CARE_SERVICE_CODE)
        self.blood_pressure = self.check_for_service(NHS_UK_BLOOD_PRESSURE_SERVICE_CODE)
        self.contraception = self.check_for_service(NHS_UK_CONTRACEPTION_SERVICE_CODE)

    def __repr__(self: Self) -> str:
        """Returns a string representation of the object."""
        return f"<NHSEntity: name={self.org_name} odscode={self.odscode}>"

    def normal_postcode(self: Self) -> str:
        """Returns the postcode in a normalised format."""
        return self.postcode.replace(" ", "").upper()

    def extract_contact(self: Self, contact_type: str) -> str | None:
        """Returns the nested contact value within the input payload."""
        return next(
            (
                item.get("ContactValue")
                for item in self.entity_data.get("Contacts", [])
                if (
                    item.get("ContactMethodType", "").upper() == contact_type.upper()
                    and item.get("ContactType", "").upper() == "PRIMARY"
                    and item.get("ContactAvailabilityType", "").upper() == "OFFICE HOURS"
                )
            ),
            None,
        )

    def check_for_uec_service(self: Self, service_code: str) -> bool | None:
        """Checks if the UEC service exists in the payload.

        Args:
            service_code (str): NHS UK Service Code of the UEC service to extract if exists

        Returns:
            Union[bool, None]: True if the service exists, False otherwise
        """
        return self._extract_service_from_list("UecServices", service_code)

    def check_for_service(self: Self, service_code: str) -> bool | None:
        """Checks if the service exists in the payload.

        Args:
            service_code (str): NHS UK Service Code of the service to extract if exists

        Returns:
            Union[bool, None]: True if the service exists, False otherwise
        """
        return self._extract_service_from_list("Services", service_code)

    def _extract_service_from_list(self: Self, list_name: str, service_code: str) -> bool | None:
        if isinstance(self.entity_data.get(list_name, []), list):
            return any(item.get("ServiceCode") == service_code for item in self.entity_data.get(list_name, []))
        return None

    def _get_standard_opening_times(self: Self) -> StandardOpeningTimes:
        """Get the standard opening times.

        Filters the raw opening times data for standard weekly opening
        times and returns it in a StandardOpeningTimes object.

        Args:
            opening_time_type (str): Opening times type (General/Additional)

        Returns:
            StandardOpeningTimes: NHS UK standard opening times
        """
        std_opening_times = StandardOpeningTimes()
        for open_time in filter(is_std_opening_json, self.entity_data.get("OpeningTimes", [])):
            weekday = open_time["Weekday"].lower()

            # Populate StandardOpeningTimes obj depending on IsOpen status
            if open_time["IsOpen"]:
                open_period = OpenPeriod.from_string_times(open_time["OpeningTime"], open_time["ClosingTime"])
                std_opening_times.add_open_period(open_period, weekday)
            else:
                std_opening_times.explicit_closed_days.add(weekday)

        return std_opening_times

    def _get_specified_opening_times(self: Self) -> list[SpecifiedOpeningTime]:
        """Get all the Specified Opening Times.

        Args:
            opening_time_type (str): OpeningTimeType to filter the data, General for pharmacy

        Returns:
            dict: key=date and value = List[OpenPeriod] objects in a sort order
        """
        specified_times_list = list(filter(is_spec_opening_json, self.entity_data.get("OpeningTimes", [])))
        specified_times_list = sorted(specified_times_list, key=lambda item: item["AdditionalOpeningDate"])
        specified_opening_times = []

        # Grouping data by date, and create open_period objects from values
        for date_str, op_dict_list in groupby(specified_times_list, lambda item: (item["AdditionalOpeningDate"])):
            open_periods = []
            date = datetime.strptime(date_str, "%b  %d  %Y").date()
            is_open = True

            for item in list(op_dict_list):
                if item["IsOpen"]:
                    open_periods.append(OpenPeriod.from_string_times(item["OpeningTime"], item["ClosingTime"]))
                else:
                    is_open = False

            specified_opening_times.append(SpecifiedOpeningTime(open_periods, date, is_open))

        return specified_opening_times

    def is_status_hidden_or_closed(self: Self) -> bool:
        """Check if the status is hidden or closed. If so, return True.

        Returns:
            bool: True if status is hidden or closed, False otherwise
        """
        return self.org_status.upper() in CLOSED_AND_HIDDEN_STATUSES

    def all_times_valid(self: Self) -> bool:
        """Does checks on all opening times for correct format, business rules, overlaps."""
        # Check format matches either spec or std format
        for item in self.entity_data.get("OpeningTimes", []):
            if not (is_std_opening_json(item) or is_spec_opening_json(item)):
                return False

        # Check validity of both types of open times
        return self.standard_opening_times.is_valid() and SpecifiedOpeningTime.valid_list(self.specified_opening_times)

    def is_matching_dos_service(self: Self, dos_service: DoSService) -> bool:
        """Check if the entity matches the DoS service.

        Args:
            dos_service (DoSService): DoS service to check against

        Returns:
            bool: True if the entity matches the DoS service, False otherwise
        """
        if None in (self.odscode, dos_service.odscode):
            return False

        if dos_service.typeid in PHARMACY_SERVICE_TYPE_IDS:
            return (
                len(dos_service.odscode) >= 5  # noqa: PLR2004
                and len(self.odscode) >= 5  # noqa: PLR2004
                and dos_service.odscode[:5] == self.odscode[:5]
            )

        logger.warning(f"Failed nhs code match check for unknown typeid '{dos_service.typeid}'")
        return False


def is_std_opening_json(item: dict) -> bool:
    """Checks EXACT match to definition of General/Standard opening time for NHS Open time payload object."""
    # Check values
    if (
        str(item.get("OpeningTimeType")).upper() != "GENERAL"
        or str(item.get("Weekday")).lower() not in WEEKDAYS
        or item.get("AdditionalOpeningDate") not in [None, ""]
    ):
        return False

    is_open = item.get("IsOpen")
    if not isinstance(is_open, bool):
        return False

    open_time = item.get("OpeningTime")
    close_time = item.get("ClosingTime")

    # If marked as open, ensure open time values are valid
    if is_open and OpenPeriod.from_string_times(open_time, close_time) is None:
        return False

    # If marked as closed, ensure open time values are not present
    return bool(
        is_open or all(value in ["", None] for value in (open_time, close_time)),
    )


def is_spec_opening_json(item: dict) -> bool:
    """Checks EXACT match to definition of Additional/Spec opening time for NHS Open time payload object."""
    if str(item.get("OpeningTimeType")).upper() != "ADDITIONAL":
        return False

    try:
        datetime.strptime(str(item.get("AdditionalOpeningDate")), "%b  %d  %Y")
    except ValueError:
        return False

    is_open = item.get("IsOpen")
    if not isinstance(is_open, bool):
        return False

    open_time = item.get("OpeningTime")
    close_time = item.get("ClosingTime")

    # If marked as open, ensure open time values are valid
    if is_open and OpenPeriod.from_string_times(open_time, close_time) is None:
        return False

    # If marked as closed, ensure open time values are not present
    return bool(
        is_open or all(value in ["", None] for value in (open_time, close_time)),
    )


def skip_if_key_is_none(key: None | str | bool | int) -> bool:
    """If the key is None, skip the item."""
    return key is None


def get_palliative_care_log_value(palliative_care: bool, skip_palliative_care: bool) -> bool | str:
    """Get the value to log for palliative care.

    Args:
        palliative_care (bool): The value of palliative care
        skip_palliative_care (bool): Whether to skip palliative care

    Returns:
    bool | str: The value to log
    """
    return (
        "Never been updated on Profile Manager, skipped palliative care checks"
        if skip_palliative_care
        else palliative_care
    )
