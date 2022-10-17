from dataclasses import dataclass


@dataclass(init=True, repr=True)
class DoSLocation:
    """A Class to represent a location in the UK store within the DoS Database locations table"""

    id: int
    postcode: str
    easting: float
    northing: float
    postaltown: str
    latitude: float
    longitude: float

    def normal_postcode(self) -> str:
        return self.postcode.replace(" ", "").upper()

    def is_valid(self) -> bool:
        return None not in (self.easting, self.northing, self.latitude, self.longitude)
