from dataclasses import dataclass


@dataclass
class ChangeEvent:
    address: str
    website: str
    phone: str  # Public phone number
    standard_opening_times: str
    specified_opening_times: str
