from dataclasses import dataclass
from json import load


@dataclass(init=True, repr=True)
class ChangeEvent:
    """A change event."""

    address: str
    website: str
    phone: str  # Public phone number
    standard_opening_times: str
    specified_opening_times: str

    def create_change_event(self) -> dict:
        """Create a change event from base including the set attributes."""
        base_change_event = load("base_change_event.json")
        base_change_event["Address1"] = self.address
        return base_change_event
