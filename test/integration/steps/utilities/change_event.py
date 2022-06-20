import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4

from dateutil.relativedelta import relativedelta

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


@dataclass(repr=True)
class ChangeEvent:
    odscode: str | None
    organisation_name: str | None
    organisation_type_id: str | None
    organisation_sub_type: str | None
    address_line_1: str | None
    address_line_2: str | None
    address_line_3: str | None
    city: str | None
    county: str | None
    postcode: str | None
    website: str | None
    phone: str | None
    standard_opening_times: List[Dict[str, Any]] | None
    specified_opening_times: List[Dict[str, Any]] | None
    unique_key: str = ""

    def __init__(
        self,
        odscode: str | None = None,
        organisation_name: str | None = None,
        organisation_type_id: str | None = None,
        organisation_sub_type: str | None = None,
        address_line_1: str | None = None,
        address_line_2: str | None = None,
        address_line_3: str | None = None,
        city: str | None = None,
        county: str | None = None,
        postcode: str | None = None,
        website: str | None = None,
        phone: str | None = None,
        standard_opening_times: None = None,
        specified_opening_times: None = None,
        unique_key: str = "",
    ) -> None:
        self.odscode = odscode
        self.organisation_name = organisation_name
        self.organisation_type_id = organisation_type_id
        self.organisation_sub_type = organisation_sub_type
        self.address_line_1 = address_line_1
        self.address_line_2 = address_line_2
        self.address_line_3 = address_line_3
        self.city = city
        self.county = county
        self.postcode = postcode
        self.website = website
        self.phone = phone
        self.standard_opening_times = standard_opening_times
        self.specified_opening_times = specified_opening_times
        self.unique_key = unique_key

    def build_contacts(self) -> List[None | Dict[str, Any]]:
        contacts: List = []
        if self.website is not None:
            contacts.append(
                {
                    "ContactType": "Primary",
                    "ContactAvailabilityType": "Office hours",
                    "ContactMethodType": "Website",
                    "ContactValue": self.website,
                }
            )
        if self.phone is not None:
            contacts.append(
                {
                    "ContactType": "Primary",
                    "ContactAvailabilityType": "Office hours",
                    "ContactMethodType": "Telephone",
                    "ContactValue": self.phone,
                }
            )
        return contacts

    def build_opening_times(self) -> List[None | Dict[str, Any]]:
        if self.standard_opening_times is None and self.specified_opening_times is None:
            return []
        elif self.standard_opening_times is not None and self.specified_opening_times is None:
            return self.standard_opening_times
        elif self.standard_opening_times is None and self.specified_opening_times is not None:
            return self.specified_opening_times
        else:
            return self.standard_opening_times + self.specified_opening_times

    def get_change_event(self):
        return {
            "ODSCode": self.odscode,
            "OrganisationName": self.organisation_name,
            "OrganisationTypeId": self.organisation_type_id,
            "OrganisationSubType": self.organisation_sub_type,
            "OrganisationStatus": "Visible",
            "Address1": self.address_line_1,
            "Address2": self.address_line_2,
            "Address3": self.address_line_3,
            "City": self.city,
            "County": self.county,
            "Postcode": self.postcode,
            "OpeningTimes": self.build_opening_times(),
            "Contacts": self.build_contacts(),
        }


class ChangeEventBuilder:
    service_type: str
    change_event: ChangeEvent

    def __init__(self, service_type: str):
        self.service_type = service_type
        self.build_change_event_from_default()
        self.make_change_event_unique()

    def build_change_event_from_default(self):
        self.change_event = ChangeEvent(
            odscode=self.get_default_random_odscode(),
            organisation_name="Test Organisation",
            organisation_type_id=self.get_organisation_type_id(self.service_type),
            organisation_sub_type=self.get_organisation_sub_type(self.service_type),
            address_line_1="Test Address Line 1",
            address_line_2="Test Address Line 2",
            address_line_3="Test Address Line 3",
            city="Test City",
            county="Test County",
            postcode="TES T12",
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
                {
                    "Weekday": "",
                    "OpeningTime": "10:00",
                    "ClosingTime": "17:00",
                    "OpeningTimeType": "Additional",
                    "AdditionalOpeningDate": "Dec 25 2022",
                    "IsOpen": True,
                },
            ],
        )

    def build_same_as_dos_change_event_by_ods(self, ods_code: str):
        change_event = self.change_event.get_change_event()
        match self.service_type.upper():
            case ServiceTypeAliases.PHARMACY_TYPE_ALIAS:
                change_event["ODSCode"] = ods_code
                demographics_data = get_change_event_demographics(change_event["ODSCode"], PHARMACY_ORG_TYPE_ID)
                org_type_id = PHARMACY_ORG_TYPE_ID
                org_sub_type = PHARMACY_SUB_TYPE
            case ServiceTypeAliases.DENTIST_TYPE_ALIAS:
                change_event["ODSCode"] = ods_code
                demographics_data = get_change_event_demographics(change_event["ODSCode"], DENTIST_ORG_TYPE_ID)
                org_type_id = DENTIST_ORG_TYPE_ID
                org_sub_type = DENTIST_SUB_TYPE
            case _:
                raise ValueError(f"Service type {self.service_type} does not exist")
        print(f"Latest selected ODSCode: {change_event['ODSCode']}")
        change_event["OrganisationTypeId"] = org_type_id
        change_event["OrganisationSubType"] = org_sub_type
        change_event["OrganisationName"] = demographics_data["publicname"]
        change_event["Postcode"] = demographics_data["postcode"]
        change_event["Contacts"][0]["ContactValue"] = demographics_data["web"]
        change_event["Contacts"][1]["ContactValue"] = demographics_data["publicphone"]
        address_keys = ["Address1", "Address2", "Address3", "City", "County"]
        for address_key in address_keys:
            change_event[address_key] = None
        address_parts = demographics_data["address"].split("$", 4)
        counter = 0
        for address_part in address_parts:
            change_event[address_keys[counter]] = address_part
            counter += 1
        standard_opening_times = get_change_event_standard_opening_times(demographics_data["id"])
        change_event["OpeningTimes"] = []
        for day in standard_opening_times:
            for opening_times in standard_opening_times[day]:
                change_event["OpeningTimes"].append(
                    {
                        "Weekday": day,
                        "OpeningTime": opening_times["start_time"],
                        "ClosingTime": opening_times["end_time"],
                        "OpeningTimeType": "General",
                        "AdditionalOpeningDate": "",
                        "IsOpen": True,
                    }
                )
        specified_opening_times = get_change_event_specified_opening_times(demographics_data["id"])
        for date in specified_opening_times:
            for opening_times in specified_opening_times[date]:
                str_date = datetime.strptime(date, "%Y-%m-%d")
                change_event["OpeningTimes"].append(
                    {
                        "Weekday": "",
                        "OpeningTime": opening_times["start_time"],
                        "ClosingTime": opening_times["end_time"],
                        "OpeningTimeType": "Additional",
                        "AdditionalOpeningDate": str_date.strftime("%b %d %Y"),
                        "IsOpen": True,
                    }
                )
        return change_event

    def make_change_event_unique(self):
        self.change_event.unique_key = str(uuid4())

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


def valid_change_event(change_event: dict) -> bool:
    """This function checks if the data stored in DoS would pass the change request
    validation within DoS API Gateway"""
    if not re.fullmatch(
        r"(https?:\/\/)?([a-z\d][a-z\d-]*[a-z\d]\.)+[a-z]{2,}(\/.*)?",
        str(change_event["Contacts"][0]["ContactValue"]),
    ):  # Website
        return False
    if not re.fullmatch(r"[+0][0-9 ()]{9,}", str(change_event["Contacts"][1]["ContactValue"])):  # Phone
        return False
    return True


def build_same_as_dos_change_event(service_type: str):
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


def set_opening_times_change_event(service_type: str):
    change_event: ChangeEvent = ChangeEventBuilder(service_type).change_event
    change_event: Dict = change_event.get_change_event()
    date = datetime.today() + relativedelta(months=1)
    has_set_closed_day = False
    for day in change_event["OpeningTimes"]:
        if day["IsOpen"] and day["OpeningTimeType"] == "General":
            closed_day = day["Weekday"]
            has_set_closed_day = True
            break
    if has_set_closed_day is False:
        raise ValueError("ERROR!.. Unable to find 'Open' Standard opening time")
    change_event["OpeningTimes"] = list(filter(lambda day: day["Weekday"] != closed_day, change_event["OpeningTimes"]))
    change_event["OpeningTimes"].append(
        {
            "Weekday": closed_day,
            "OpeningTime": "",
            "ClosingTime": "",
            "Times": "-",
            "OffsetOpeningTime": 0,
            "OffsetClosingTime": 0,
            "OpeningTimeType": "General",
            "AdditionalOpeningDate": "",
            "IsOpen": False,
        }
    )
    change_event["OpeningTimes"].append(
        {
            "Weekday": "",
            "OpeningTime": "",
            "ClosingTime": "",
            "Times": "-",
            "OffsetOpeningTime": 0,
            "OffsetClosingTime": 0,
            "OpeningTimeType": "Additional",
            "AdditionalOpeningDate": date.strftime("%b %d %Y"),
            "IsOpen": False,
        }
    )
    return change_event
