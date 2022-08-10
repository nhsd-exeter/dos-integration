import re
from datetime import datetime
from typing import Dict
from uuid import uuid4

from dateutil.relativedelta import relativedelta

from .change_event import ChangeEvent
from .constants import (
    DENTIST_ORG_TYPE_ID,
    DENTIST_SUB_TYPE,
    PHARMACY_ORG_TYPE_ID,
    PHARMACY_SUB_TYPE,
    ServiceTypeAliases,
)
from .utils import (
    get_change_event_demographics,
    get_change_event_specified_opening_times,
    get_change_event_standard_opening_times,
    get_single_service_pharmacy,
    random_dentist_odscode,
    random_pharmacy_odscode,
)


class ChangeEventBuilder:
    service_type: str
    _change_event: ChangeEvent

    def __init__(self, service_type: str):
        self.service_type = service_type

    def build_change_event_from_default(self):
        self._change_event = ChangeEvent(
            odscode=self.get_default_random_odscode(),
            organisation_name="Test Organisation",
            organisation_type_id=self.get_organisation_type_id(self.service_type),
            organisation_sub_type=self.get_organisation_sub_type(self.service_type),
            address_line_1="Test Address Line 1",
            address_line_2="Test Address Line 2",
            address_line_3="Test Address Line 3",
            city="Test City",
            county="Test County",
            postcode="BS5 9SJ",
            website="https://www.test.com",
            phone="01234 567 890",
            standard_opening_times=[
                {
                    "Weekday": "Monday",
                    "OpeningTime": "07:30",
                    "ClosingTime": "23:00",
                    "OpeningTimeType": "General",
                    "IsOpen": True,
                },
                {
                    "Weekday": "Tuesday",
                    "OpeningTime": "07:30",
                    "ClosingTime": "23:00",
                    "OpeningTimeType": "General",
                    "IsOpen": True,
                },
                {
                    "Weekday": "Wednesday",
                    "OpeningTime": "07:30",
                    "ClosingTime": "23:00",
                    "OpeningTimeType": "General",
                    "IsOpen": True,
                },
                {
                    "Weekday": "Thursday",
                    "OpeningTime": "07:30",
                    "ClosingTime": "23:00",
                    "OpeningTimeType": "General",
                    "IsOpen": True,
                },
                {
                    "Weekday": "Friday",
                    "OpeningTime": "07:30",
                    "ClosingTime": "23:00",
                    "OpeningTimeType": "General",
                    "IsOpen": True,
                },
                {
                    "Weekday": "Saturday",
                    "OpeningTime": "07:30",
                    "ClosingTime": "23:00",
                    "OpeningTimeType": "General",
                    "IsOpen": True,
                },
                {
                    "Weekday": "Sunday",
                    "OpeningTime": "10:00",
                    "ClosingTime": "17:00",
                    "OpeningTimeType": "General",
                    "IsOpen": True,
                },
            ],
            specified_opening_times=[
                {
                    "Weekday": "",
                    "OpeningTime": "10:00",
                    "ClosingTime": "17:00",
                    "OpeningTimeType": "Additional",
                    "AdditionalOpeningDate": "Dec 24 2022",
                    "IsOpen": True,
                },
            ],
        )
        return self._change_event

    def build_same_as_dos_change_event_by_ods(self, ods_code: str) -> ChangeEvent:
        change_event: ChangeEvent = ChangeEvent()
        match self.service_type.upper():
            case ServiceTypeAliases.PHARMACY_TYPE_ALIAS:
                change_event.odscode = ods_code
                demographics_data = get_change_event_demographics(change_event.odscode, PHARMACY_ORG_TYPE_ID)
                change_event.organisation_type_id = PHARMACY_ORG_TYPE_ID
                change_event.organisation_sub_type = PHARMACY_SUB_TYPE
            case ServiceTypeAliases.DENTIST_TYPE_ALIAS:
                change_event.odscode = ods_code
                demographics_data = get_change_event_demographics(change_event.odscode, DENTIST_ORG_TYPE_ID)
                change_event.organisation_type_id = DENTIST_ORG_TYPE_ID
                change_event.organisation_sub_type = DENTIST_SUB_TYPE
            case _:
                raise ValueError(f"Service type {self.service_type} does not exist")
        change_event.organisation_name = demographics_data["publicname"]
        change_event.postcode = demographics_data["postcode"]
        change_event.website = demographics_data["web"]
        change_event.phone = demographics_data["publicphone"]
        change_event = self.set_same_as_dos_address(change_event, demographics_data["address"])
        standard_opening_times = get_change_event_standard_opening_times(demographics_data["id"])
        change_event.standard_opening_times = []
        change_event.specified_opening_times = []
        for day in standard_opening_times:
            for opening_times in standard_opening_times[day]:
                change_event.standard_opening_times.append(
                    {
                        "Weekday": day,
                        "OpeningTime": opening_times["start_time"],
                        "ClosingTime": opening_times["end_time"],
                        "OpeningTimeType": "General",
                        "IsOpen": True,
                    }
                )
        specified_opening_times = get_change_event_specified_opening_times(demographics_data["id"])
        for date in specified_opening_times:
            for opening_times in specified_opening_times[date]:
                str_date = datetime.strptime(date, "%Y-%m-%d")
                change_event.specified_opening_times.append(
                    {
                        "OpeningTime": opening_times["start_time"],
                        "ClosingTime": opening_times["end_time"],
                        "OpeningTimeType": "Additional",
                        "AdditionalOpeningDate": str_date.strftime("%b %d %Y"),
                        "IsOpen": True,
                    }
                )
        return change_event

    def make_change_event_unique(self):
        self._change_event.unique_key = str(uuid4())

    def get_default_random_odscode(self) -> str:
        match self.service_type.upper():
            case ServiceTypeAliases.PHARMACY_TYPE_ALIAS:
                ods_code = random_pharmacy_odscode()
            case ServiceTypeAliases.DENTIST_TYPE_ALIAS:
                ods_code = random_dentist_odscode()
            case _:
                raise ValueError(f"Service type {self.service_type} does not exist")
        return ods_code

    @staticmethod
    def get_organisation_type_id(service_type: str) -> str:
        match service_type.upper():
            case ServiceTypeAliases.PHARMACY_TYPE_ALIAS:
                organisation_type_id = PHARMACY_ORG_TYPE_ID
            case ServiceTypeAliases.DENTIST_TYPE_ALIAS:
                organisation_type_id = DENTIST_ORG_TYPE_ID
            case _:
                raise ValueError(f"Service type {service_type} does not exist")
        return organisation_type_id

    @staticmethod
    def get_organisation_sub_type(service_type: str) -> str:
        match service_type.upper():
            case ServiceTypeAliases.PHARMACY_TYPE_ALIAS:
                organisation_sub_type = PHARMACY_SUB_TYPE
            case ServiceTypeAliases.DENTIST_TYPE_ALIAS:
                organisation_sub_type = DENTIST_SUB_TYPE
            case _:
                raise ValueError(f"Service type {service_type} does not exist")
        return organisation_sub_type

    def set_same_as_dos_address(self, change_event: ChangeEvent, address: str) -> ChangeEvent:
        address_parts = address.split("$", 4)
        if len(address_parts) < 5:
            number_of_unused_address_parts = 5 - len(address_parts)
            for _ in range(number_of_unused_address_parts):
                address_parts.append(None)

        change_event.build_address_lines(
            address_line_1=address_parts[0],
            address_line_2=address_parts[1],
            address_line_3=address_parts[2],
            city=address_parts[3],
            county=address_parts[4],
        )
        return change_event


def valid_change_event(change_event: ChangeEvent) -> bool:
    """This function checks if the data stored in DoS would pass the change request
    validation within DoS API Gateway"""
    if change_event.website is not None and not re.fullmatch(
        r"(https?:\/\/)?([a-z\d][a-z\d-]*[a-z\d]\.)+[a-z]{2,}(\/.*)?",
        change_event.website,
    ):
        return False
    if change_event.phone is not None and not re.fullmatch(r"[+0][0-9 ()]{9,}", change_event.phone):
        return False
    return True


def build_same_as_dos_change_event(service_type: str) -> ChangeEvent:
    while True:
        match service_type.upper():
            case ServiceTypeAliases.DENTIST_TYPE_ALIAS:
                ods_code = random_dentist_odscode()
            case ServiceTypeAliases.PHARMACY_TYPE_ALIAS:
                ods_code = get_single_service_pharmacy()
            case _:
                raise ValueError(f"Service type {service_type} does not exist")
        change_event: Dict = ChangeEventBuilder(service_type).build_same_as_dos_change_event_by_ods(ods_code)
        if valid_change_event(change_event):
            break
    return change_event


def set_opening_times_change_event(service_type: str) -> ChangeEvent:
    change_event: ChangeEvent = ChangeEventBuilder(service_type).build_change_event_from_default()
    date = datetime.today() + relativedelta(months=1)
    has_set_closed_day = False
    for day in change_event.standard_opening_times:
        if day["IsOpen"] and day["OpeningTimeType"] == "General":
            closed_day = day["Weekday"]
            has_set_closed_day = True
            break
    if has_set_closed_day is False:
        raise ValueError("ERROR!.. Unable to find 'Open' Standard opening time")
    change_event.standard_opening_times = list(
        filter(lambda day: day["Weekday"] != closed_day, change_event.standard_opening_times)
    )
    change_event.standard_opening_times.append(
        {
            "Weekday": closed_day,
            "OpeningTime": "",
            "ClosingTime": "",
            "OffsetOpeningTime": 0,
            "OffsetClosingTime": 0,
            "OpeningTimeType": "General",
            "AdditionalOpeningDate": "",
            "IsOpen": False,
        }
    )
    change_event.specified_opening_times.append(
        {
            "Weekday": "",
            "OpeningTime": "",
            "ClosingTime": "",
            "OffsetOpeningTime": 0,
            "OffsetClosingTime": 0,
            "OpeningTimeType": "Additional",
            "AdditionalOpeningDate": date.strftime("%b %d %Y"),
            "IsOpen": False,
        }
    )
    change_event.specified_opening_times.append(
        {
            "Weekday": "",
            "OpeningTime": "",
            "ClosingTime": "",
            "OffsetOpeningTime": 0,
            "OffsetClosingTime": 0,
            "OpeningTimeType": "Additional",
            "AdditionalOpeningDate": date.strftime("%b %d %Y"),
            "IsOpen": False,
        }
    )
    return change_event
