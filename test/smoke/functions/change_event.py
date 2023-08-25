from dataclasses import dataclass, field
from datetime import datetime
from json import load


@dataclass(init=True, repr=True)
class ChangeEvent:
    """A change event."""

    address: str
    website: str
    phone: str  # Public phone number
    standard_opening_times: field(default_factory=list)
    specified_opening_times: field(default_factory=list)

    def create_change_event(self) -> dict:
        """Create a change event from the base change event and set the attributes.

        Returns:
            dict: The change event
        """
        """Create a change event from base including the set attributes."""
        base_change_event = self._load_base_change_event()
        base_change_event = self._set_address(base_change_event)
        base_change_event = self._set_contact_details(base_change_event, "Website", self.website)
        base_change_event = self._set_contact_details(base_change_event, "Telephone", self.phone)
        return self._set_opening_times(base_change_event)


    def _load_base_change_event(self) -> dict:
        """Load the base change event from the JSON file.

        Returns:
            dict: The base change event
        """
        with open("./functions/base_change_event.json") as base_change_event_file:
            return load(base_change_event_file)

    def _set_address(self, base_change_event: dict) -> dict:
        """Set the address attributes on the change event.

        Args:
            base_change_event (dict): The base change event

        Returns:
            dict: The change event
        """
        address_line_1, address_line_2, address_line_3, city, county = self._split_dos_address(self.address)
        base_change_event["Address1"] = address_line_1
        base_change_event["Address2"] = address_line_2
        base_change_event["Address3"] = address_line_3
        base_change_event["City"] = city
        base_change_event["County"] = county
        return base_change_event

    def _set_contact_details(self, base_change_event: dict, change_event_name: str, value: str) -> dict:
        """Set the contact details attributes on the change event.

        Args:
            base_change_event (dict): The base change event
            change_event_name (str): The name of the change event
            value (str): The value of the change event

        Returns:
            dict: The change event
        """
        base_change_event["Contacts"].append(
            {
                "ContactType": "Primary",
                "ContactAvailabilityType": "Office hours",
                "ContactMethodType": change_event_name,
                "ContactValue": value,
            },
        )
        return base_change_event

    def _split_dos_address(self, dos_address: str) -> tuple[str, str, str, str, str]:
        """Split a DoS address into its constituent parts.

        Args:
            dos_address (str): The DoS address to split

        Returns:
            tuple[str, str, str, str, str]: The address line 1, address line 2, address line 3, city and county
        """
        dos_address = dos_address.split("$", 4)
        address_line_1 = ""
        address_line_2 = ""
        address_line_3 = ""
        city = ""
        county = ""
        match len(dos_address):
            case 1:
                address_line_1 = dos_address[0]
            case 2:
                address_line_1 = dos_address[0]
                address_line_2 = dos_address[1]
            case 3:
                address_line_1 = dos_address[0]
                address_line_2 = dos_address[1]
                address_line_3 = dos_address[2]
            case 4:
                address_line_1 = dos_address[0]
                address_line_2 = dos_address[1]
                address_line_3 = dos_address[2]
                city = dos_address[3]
            case 5:
                address_line_1 = dos_address[0]
                address_line_2 = dos_address[1]
                address_line_3 = dos_address[2]
                city = dos_address[3]
                county = dos_address[4]
            case _:
                msg = f"DoS address '{dos_address}' is not in the correct format"
                raise ValueError(msg)

        return address_line_1, address_line_2, address_line_3, city, county

    def _set_opening_times(self, base_change_event: dict) -> dict:
        """Set the opening times attributes on the change event.

        Args:
            base_change_event (dict): The base change event

        Returns:
            dict: The change event
        """
        base_change_event["OpeningTimes"].extend(
            {
                "ClosingTime": day["close"],
                "IsOpen": day["open_or_closed"],
                "OpeningTime": day["open"],
                "OpeningTimeType": "General",
                "Weekday": day["day"],
            }
            for day in self.standard_opening_times
        )

        for specified_opening_date in self.specified_opening_times:
            if isinstance(specified_opening_date["date"], str):
                specified_opening_date["date"] = datetime.strptime(specified_opening_date["date"], "%Y-%m-%d").date()

        base_change_event["OpeningTimes"].extend(
            {
                "AdditionalOpeningDate": specified_opening_date["date"].strftime("%b %d %Y"),
                "ClosingTime": specified_opening_date["close"],
                "IsOpen": specified_opening_date["open_or_closed"],
                "OpeningTime": specified_opening_date["open"],
                "OpeningTimeType": "Additional",
            }
            for specified_opening_date in self.specified_opening_times
        )
        return base_change_event
