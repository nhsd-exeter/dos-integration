from json import load
from random import choice
from time import time_ns
from typing import Self

from .data import CLOSE_TIMES, DAYS, POSTCODES, SPECIFIED_OPENING_DATES, START_TIMES


class ChangeEvent:
    """A class to represent a change event."""

    # Demographics - Contact
    website: str
    public_phone: str

    # Demographics - Location
    address: str
    postcode: str

    # Opening times
    standard_opening_times: dict[str, dict[str, str]]
    specific_opening_times: dict[str, dict[str, str]]

    # Service types
    palliative_care: bool
    blood_pressure: bool
    contraception: bool

    # Change event json
    _change_event_json: dict[str, str]

    def __init__(self: Self) -> None:
        """Initialise the class."""
        with open("resources/change_event.json", "r+") as file:
            file_contents = load(file)
            self.website = file_contents["Contacts"][0]["ContactValue"]
            self.public_phone = file_contents["Contacts"][1]["ContactValue"]
            self.address = file_contents["Address1"]
            self.postcode = file_contents["Postcode"]
        self.standard_opening_times = {}
        self.specific_opening_times = {}
        self.palliative_care = False
        self.blood_pressure = False
        self.contraception = False

    def cause_contact_updates(self: Self) -> None:
        """Cause a location update."""
        self.website = f"{self.website} {time_ns()}"
        self.public_phone = f"{self.public_phone} {time_ns()}"

    def cause_location_updates(self: Self) -> None:
        """Cause a location update."""
        self.address = f"{self.address} {time_ns()}"
        self.postcode = choice(POSTCODES)

    def cause_opening_times_updates(self: Self) -> None:
        """Cause an opening times update."""
        self.standard_opening_times = {
            choice(DAYS): {
                "OpeningTime": choice(START_TIMES),
                "ClosingTime": choice(CLOSE_TIMES),
            },
        }
        self.specific_opening_times = {
            choice(SPECIFIED_OPENING_DATES): {
                "OpeningTime": choice(START_TIMES),
                "ClosingTime": choice(CLOSE_TIMES),
            },
        }

    def cause_palliative_care_updates(self: Self) -> None:
        """Cause a palliative care update."""
        self.palliative_care = True

    def cause_blood_pressure_updates(self: Self) -> None:
        """Cause a blood pressure update."""
        self.blood_pressure = True

    def cause_contraception_updates(self: Self) -> None:
        """Cause a contraception update."""
        self.contraception = True

    def create_change_event_json(self: Self) -> dict[str, str]:
        """Create a change event json payload."""
        with open("resources/change_event.json", "r+") as file:
            file_contents = load(file)
            file_contents["Contacts"][0]["ContactValue"] = self.website
            file_contents["Contacts"][1]["ContactValue"] = self.public_phone
            file_contents["Address1"] = self.address
            file_contents["Postcode"] = self.postcode
            file_contents["OpeningTimes"] = self._update_change_event_json_with_opening_times()
            file_contents["UecServices"] = self._update_change_event_json_with_uec_services()
            file_contents["Services"] = self._update_change_event_json_with_service()
            return file_contents

    def _update_change_event_json_with_opening_times(self: Self) -> list[dict[str, str]]:
        opening_times = [
            {
                "Weekday": day,
                "OpeningTime": times["OpeningTime"],
                "ClosingTime": times["ClosingTime"],
                "OpeningTimeType": "General",
                "IsOpen": True,
            }
            for day, times in self.standard_opening_times.items()
        ]
        opening_times.extend(
            {
                "AdditionalOpeningDate": date,
                "OpeningTime": times["OpeningTime"],
                "ClosingTime": times["ClosingTime"],
                "OpeningTimeType": "Additional",
                "IsOpen": True,
            }
            for date, times in self.specific_opening_times.items()
        )
        return opening_times

    def _update_change_event_json_with_uec_services(self: Self) -> list:
        uec_services = []
        if self.palliative_care:
            uec_services.append(
                {
                    "ServiceName": "Pharmacy palliative care medication stockholder",
                    "ServiceCode": "SRV0559",
                },
            )
        return uec_services

    def _update_change_event_json_with_service(self: Self) -> list:
        service = []
        if self.blood_pressure:
            service.append(
                {
                    "ServiceName": "NHS blood pressure check service",
                    "ServiceCode": "SRV0560",
                },
            )
        if self.contraception:
            service.append(
                {
                    "ServiceName": "NHS Pharmacy Contraception Service",
                    "ServiceCode": "SRV2000",
                },
            )
        return service
