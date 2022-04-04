from dataclasses import dataclass, field, fields
from itertools import groupby
from typing import List, Union
from common.constants import DENTIST_ORG_TYPE_ID, PHARMACY_ORG_TYPE_ID

from aws_lambda_powertools import Logger

from .dos_db_connection import query_dos_db
from .opening_times import OpenPeriod, SpecifiedOpeningTime, StandardOpeningTimes

VALID_STATUS_ID = 1
logger = Logger(child=True)
dos_location_cache = {}


class DoSService:
    """Class to represent a DoS Service"""

    # These values are which columns are selected from the database and then
    # are passed in as attributes into the DoSService object.
    db_columns = [
        "id",
        "uid",
        "name",
        "odscode",
        "address",
        "town",
        "postcode",
        "web",
        "email",
        "fax",
        "nonpublicphone",
        "typeid",
        "parentid",
        "subregionid",
        "statusid",
        "createdtime",
        "modifiedtime",
        "publicphone",
        "publicname",
    ]

    def __init__(self, db_cursor_row: tuple) -> None:
        """Sets the attributes of this object to those found in the db row
        Args:
            db_cursor_row (dict): Change Request changes
        """
        for i, attribute_name in enumerate(self.db_columns):
            attribute_value = db_cursor_row[i]
            setattr(self, attribute_name, attribute_value)

        # Do not use these, access them via their corresponding methods
        self._standard_opening_times = None
        self._specified_opening_times = None

    def __repr__(self) -> str:
        """Returns a string representation of this object"""
        if self.publicname is not None:
            name = self.publicname
        elif self.name is not None:
            name = self.name
        else:
            name = "NO-VALID-NAME"

        return (
            f"<DoSService: name='{name[0:16]}' id={self.id} uid={self.uid} "
            f"odscode={self.odscode} type={self.typeid} status={self.statusid}>"
        )

    def normal_postcode(self) -> str:
        return self.postcode.replace(" ", "").upper()

    def get_standard_opening_times(self) -> StandardOpeningTimes:
        """Retrieves values from db on first call. Returns stored values on subsequent calls"""
        if self._standard_opening_times is None:
            self._standard_opening_times = get_standard_opening_times_from_db(self.id)
        return self._standard_opening_times

    def get_specified_opening_times(self) -> List[SpecifiedOpeningTime]:
        """Retrieves values from db on first call. Returns stored values on subsequent calls"""
        if self._specified_opening_times is None:
            self._specified_opening_times = get_specified_opening_times_from_db(self.id)
        return self._specified_opening_times

    def any_generic_bankholiday_open_periods(self) -> bool:
        return len(self.get_standard_opening_times().generic_bankholiday) > 0


@dataclass(init=True, repr=True)
class DoSLocation:
    id: int
    postcode: str
    easting: int
    northing: int
    latitude: float
    longitude: float
    postaltown: str = field(default=None)

    def normal_postcode(self) -> str:
        return self.postcode.replace(" ", "").upper()

    def is_valid(self) -> bool:
        return None not in (self.easting, self.northing, self.latitude, self.longitude)


def get_matching_dos_services(odscode: str, org_type_id: str) -> List[DoSService]:
    """Retrieves DoS Services from DoS database

    Args:
        odscode (str): ODScode to match on
        org_type_id (str): OrganisationType to match on

    Returns:
        list[DoSService]: List of DoSService objects with matching first 5
        digits of odscode, taken from DoS database
    """
    if org_type_id == PHARMACY_ORG_TYPE_ID:
        logger.info(
            f"Searching for '{org_type_id}' DoS services with ODSCode that matches first 5 digits of '{odscode}'"
        )
        sql_query = f"SELECT {', '.join(DoSService.db_columns)} FROM services WHERE odscode LIKE %(ODS_5)s"
        named_args = {"ODS_5": f"{odscode[0:5]}%"}
    elif org_type_id == DENTIST_ORG_TYPE_ID:
        odscode_7 = get_new_odscode_for_dentist(odscode)
        logger.info(f"Searching for '{org_type_id}' DoS services with ODSCode that matches '{odscode_7}'")
        sql_query = f"SELECT {', '.join(DoSService.db_columns)} FROM services WHERE odscode LIKE %(ODS)s"
        named_args = {"ODS": f"{odscode_7}%"}
    else:
        logger.warning(f"Found invalid nhsuk org_type_id':{org_type_id}' for a given odscode '{odscode}'")
    c = query_dos_db(query=sql_query, vars=named_args)

    # Create list of DoSService objects from returned rows
    services = [DoSService(row) for row in c.fetchall()]
    c.close()
    return services


def get_new_odscode_for_dentist(odscode: str) -> str:
    def get_odscode_6(x):
        return x[0:1] + "0" + x[1:6]

    odscode_length = len(odscode)
    if odscode_length == 10:
        return odscode[0:7]
    elif odscode_length == 9:
        return get_odscode_6(odscode[0:6])
    elif odscode_length == 7:
        return odscode
    elif odscode_length == 6:
        return get_odscode_6(odscode)
    else:
        return odscode


def get_specified_opening_times_from_db(service_id: int) -> List[SpecifiedOpeningTime]:
    """Retrieves specified opening times from  DoS database
    Args:
        serviceid (int): serviceid to match on

    Returns:
        List[SpecifiedOpeningTime]: List of Specified Opening times with
        matching serviceid
    """

    logger.info(f"Searching for specified opening times with serviceid that matches '{service_id}'")

    sql_query = (
        "SELECT ssod.serviceid, ssod.date, ssot.starttime, ssot.endtime, ssot.isclosed "
        "FROM servicespecifiedopeningdates ssod "
        "INNER JOIN servicespecifiedopeningtimes ssot "
        "ON ssod.id = ssot.servicespecifiedopeningdateid "
        "WHERE ssod.serviceid = %(service_id)s"
    )
    named_args = {"service_id": service_id}
    c = query_dos_db(sql_query, named_args)

    """sort by date and then by starttime"""
    sorted_list = sorted(c.fetchall(), key=lambda row: (row[1], row[2]))

    specified_opening_times = []
    for date, db_rows in groupby(sorted_list, lambda row: (row[1])):
        is_open = True
        open_periods = []
        for row in list(db_rows):
            if row[4] is True:  # row[4] is the 'is_closed' column
                is_open = False
            else:
                open_periods.append(OpenPeriod(row[2], row[3]))

        specified_opening_times.append(SpecifiedOpeningTime(open_periods, date, is_open))

    c.close()
    return specified_opening_times


def get_standard_opening_times_from_db(service_id: int) -> StandardOpeningTimes:
    """Retrieves standard opening times from DoS database"""

    logger.info(f"Searching for standard opening times with serviceid that matches '{service_id}'")

    sql_command = (
        "SELECT sdo.serviceid, sdo.dayid, otd.name, sdot.starttime, sdot.endtime "
        "FROM servicedayopenings sdo "
        "INNER JOIN servicedayopeningtimes sdot "
        "ON sdo.id = sdot.servicedayopeningid "
        "LEFT JOIN openingtimedays otd "
        "ON sdo.dayid = otd.id "
        "WHERE sdo.serviceid = %(service_id)s"
    )
    named_args = {"service_id": service_id}
    c = query_dos_db(sql_command, named_args)

    standard_opening_times = StandardOpeningTimes()
    for row in c.fetchall():
        weekday = row[2].lower()
        start = row[3]
        end = row[4]
        open_period = OpenPeriod(start, end)
        standard_opening_times.add_open_period(open_period, weekday)

    c.close()
    return standard_opening_times


def get_dos_locations(postcode: str) -> List[DoSLocation]:
    logger.info(f"Searching for DoS locations with postcode of '{postcode}'")

    normalised_pc = postcode.replace(" ", "").upper()
    global dos_location_cache
    if normalised_pc in dos_location_cache:
        logger.info(f"Postcode {normalised_pc} location/s found in local cache.")
        return dos_location_cache[normalised_pc]

    # Regex matches any combination of whitespace in postcode
    pc_regex = " *".join(normalised_pc)
    db_column_names = [f.name for f in fields(DoSLocation)]
    sql_command = f"SELECT {', '.join(db_column_names)} FROM locations WHERE postcode ~* %(pc_regex)s"
    named_args = {"pc_regex": pc_regex}
    c = query_dos_db(sql_command, named_args)

    dos_locations = [DoSLocation(**row) for row in c.fetchall()]
    dos_location_cache[normalised_pc] = dos_locations
    logger.debug(f"Postcode location/s for {normalised_pc} added to local cache.")

    return dos_locations


def get_valid_dos_postcode(postcode: str) -> Union[str, None]:
    """Finds the valid DoS formatted version of the given postcode. Or None if not a valid DoS postcode"""
    dos_locations = [loc for loc in get_dos_locations(postcode) if loc.is_valid()]
    if len(dos_locations) == 0:
        return None
    return dos_locations[0].postcode
