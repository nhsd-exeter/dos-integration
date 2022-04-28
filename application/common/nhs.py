from dataclasses import dataclass
from datetime import datetime
from itertools import groupby
from typing import List, Union

from aws_lambda_powertools import Logger
from common.opening_times import WEEKDAYS, OpenPeriod, SpecifiedOpeningTime, StandardOpeningTimes
from common.dos import DoSService
from common.constants import DENTIST_SERVICE_TYPE_IDS, PHARMACY_SERVICE_TYPE_IDS

logger = Logger(child=True)


@dataclass
class NHSEntity:
    """This is an object to store an NHS Entity data

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
    address_lines: List[str]
    postcode: str
    website: str
    phone: str
    standard_opening_times: Union[StandardOpeningTimes, None]
    specified_opening_times: Union[List[SpecifiedOpeningTime], None]
    CLOSED_AND_HIDDEN_STATUSES = ["HIDDEN", "CLOSED"]

    def __init__(self, entity_data: dict):
        self.entity_data = entity_data

        self.odscode = entity_data.get("ODSCode")
        self.org_name = entity_data.get("OrganisationName")
        self.org_type_id = entity_data.get("OrganisationTypeId")
        self.org_type = entity_data.get("OrganisationType")
        self.org_sub_type = entity_data.get("OrganisationSubType")
        self.org_status = entity_data.get("OrganisationStatus")
        self.odscode = entity_data.get("ODSCode")
        self.postcode = entity_data.get("Postcode")
        self.parent_org_name = entity_data.get("ParentOrganisation", {}).get("OrganisationName")
        self.city = entity_data.get("City")
        self.county = entity_data.get("County")
        self.address_lines = [
            line
            for line in [entity_data.get(x) for x in [f"Address{i}" for i in range(1, 5)] + ["City", "County"]]
            if isinstance(line, str) and line.strip() != ""
        ]

        self.standard_opening_times = self._get_standard_opening_times()
        self.specified_opening_times = self._get_specified_opening_times()
        self.phone = self.extract_contact("Telephone")
        self.website = self.extract_contact("Website")

    def __repr__(self) -> str:
        return f"<NHSEntity: name={self.org_name} odscode={self.odscode}>"

    def normal_postcode(self):
        return self.postcode.replace(" ", "").upper()

    def extract_contact(self, contact_type: str) -> Union[str, None]:
        """Returns the nested contact value within the input payload"""
        for item in self.entity_data.get("Contacts", []):
            if (
                item.get("ContactMethodType", "").upper() == contact_type.upper()
                and item.get("ContactType", "").upper() == "PRIMARY"
                and item.get("ContactAvailabilityType", "").upper() == "OFFICE HOURS"
            ):

                return item.get("ContactValue")
        return None

    def _get_standard_opening_times(self) -> StandardOpeningTimes:
        """Filters the raw opening times data for standard weekly opening
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

    def _get_specified_opening_times(self) -> List[SpecifiedOpeningTime]:
        """Get all the Specified Opening Times

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

    def is_status_hidden_or_closed(self) -> bool:
        """Check if the status is hidden or closed. If so, return True

        Returns:
            bool: True if status is hidden or closed, False otherwise
        """
        return self.org_status.upper() in self.CLOSED_AND_HIDDEN_STATUSES

    def all_times_valid(self) -> bool:
        """Does checks on all opening times for correct format, business rules, overlaps"""

        # Check format matches either spec or std format
        for item in self.entity_data.get("OpeningTimes", []):
            if not (is_std_opening_json(item) or is_spec_opening_json(item)):
                return False

        # Check validity of both types of open times
        return self.standard_opening_times.is_valid() and SpecifiedOpeningTime.valid_list(self.specified_opening_times)

    def is_matching_dos_service(self, dos_service: DoSService) -> bool:
        if None in (self.odscode, dos_service.odscode):
            return False

        if dos_service.typeid in PHARMACY_SERVICE_TYPE_IDS:
            return (len(dos_service.odscode) >= 5 and
                    len(self.odscode) >= 5 and
                    dos_service.odscode[:5] == self.odscode[:5])

        if dos_service.typeid in DENTIST_SERVICE_TYPE_IDS:
            if not (len(dos_service.odscode) >= 6 and len(self.odscode) >= 7):
                return False
            odscode_extra_0 = f"{dos_service.odscode[0]}0{dos_service.odscode[1:]}"
            return self.odscode[:7] in (dos_service.odscode[:7], odscode_extra_0[:7])

        logger.warning(f"Failed nhs code match check for unknown typeid '{dos_service.typeid}'")
        return False


def is_std_opening_json(item: dict) -> bool:
    """Checks EXACT match to definition of General/Standard opening time for NHS Open time payload object"""

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
    if not is_open and (any(value not in ["", None] for value in (open_time, close_time))):
        return False

    return True


def is_spec_opening_json(item: dict) -> bool:
    """Checks EXACT match to definition of Additional/Spec opening time for NHS Open time payload object"""

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
    if not is_open and (any(value not in ["", None] for value in (open_time, close_time))):
        return False

    return True
