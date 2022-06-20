from dataclasses import dataclass
from typing import Any, Dict, List


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
