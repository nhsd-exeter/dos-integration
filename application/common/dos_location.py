from dataclasses import dataclass


@dataclass(init=True, repr=True)
class DoSLocation:
    """A Class to represent a location in the UK store within the DoS Database locations table."""

    id: int  # noqa: A003
    postcode: str
    easting: float
    northing: float
    postaltown: str
    latitude: float
    longitude: float

    def normal_postcode(self) -> str:
        """Returns the postcode in a normalised format."""
        return self.postcode.replace(" ", "").upper()

    def is_valid(self) -> bool:
        """Returns True if the location is valid."""
        return None not in (self.easting, self.northing, self.latitude, self.longitude)
