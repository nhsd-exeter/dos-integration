from typing import TypedDict


class Demographics(TypedDict):
    """Class to represent the demographics of a service."""

    address: str
    website: str
    phone: str


class StandardOpeningTimes(TypedDict):
    """Class to represent the standard opening times of a service."""

    Monday: str
    Tuesday: str
    Wednesday: str
    Thursday: str
    Friday: str
    Saturday: str
    Sunday: str
