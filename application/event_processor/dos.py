from datetime import date, datetime
from itertools import groupby
from os import environ
from typing import Dict, List, Union
from dataclasses import dataclass, field, fields

import psycopg2
from psycopg2.extras import DictCursor
from aws_lambda_powertools import Logger

from opening_times import OpenPeriod, SpecifiedOpeningTime, StandardOpeningTimes


logger = Logger(child=True)
VALID_SERVICE_TYPES = {13, 131, 132, 134, 137}
VALID_STATUS_ID = 1

db_connection = None
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


def get_matching_dos_services(odscode: str) -> List[DoSService]:
    """Retrieves DoS Services from DoS database

    Args:
        odscode (str): ODScode to match on

    Returns:
        list[DoSService]: List of DoSService objects with matching first 5
        digits of odscode, taken from DoS database
    """

    logger.info(f"Searching for DoS services with ODSCode that matches first 5 digits of '{odscode}'")

    sql_command = f"SELECT {', '.join(DoSService.db_columns)} FROM services WHERE odscode LIKE '{odscode[0:5]}%'"
    logger.info(f"Created SQL command to run: {sql_command}")
    c = query_dos_db(sql_command)

    # Create list of DoSService objects from returned rows
    services = [DoSService(row) for row in c.fetchall()]
    c.close()
    return services


def get_specified_opening_times_from_db(service_id: int) -> List[SpecifiedOpeningTime]:
    """Retrieves specified opening times from  DoS database
    Args:
        serviceid (int): serviceid to match on

    Returns:
        List[SpecifiedOpeningTime]: List of Specified Opening times with
        matching serviceid
    """

    logger.info(f"Searching for specified opening times with serviceid that matches '{service_id}'")

    sql_command = (
        "SELECT ssod.serviceid, ssod.date, ssot.starttime, "
        "ssot.endtime, ssot.isclosed "
        "FROM servicespecifiedopeningdates ssod "
        "INNER JOIN servicespecifiedopeningtimes ssot "
        "ON ssod.serviceid = ssot.servicespecifiedopeningdateid "
        f"WHERE ssod.serviceid = {service_id}"
    )
    c = query_dos_db(sql_command)

    """sort by date and then by starttime"""
    sorted_list = sorted(c.fetchall(), key=lambda row: (row[1], row[2]))
    specified_opening_time_dict: Dict[datetime, List[OpenPeriod]] = {}
    key: date
    for key, value in groupby(sorted_list, lambda row: (row[1])):
        specified_opening_time_dict[key] = [OpenPeriod(row[2], row[3]) for row in list(value)]
    specified_opening_times = [SpecifiedOpeningTime(value, key) for key, value in specified_opening_time_dict.items()]
    c.close()
    return specified_opening_times


def get_standard_opening_times_from_db(serviceid: int) -> StandardOpeningTimes:
    """Retrieves standard opening times from DoS database"""

    logger.info(f"Searching for standard opening times with serviceid that matches '{serviceid}'")

    sql_command = (
        "SELECT sdo.serviceid,  sdo.dayid, otd.name, "
        "       sdot.starttime, sdot.endtime "
        "FROM servicedayopenings sdo "
        "INNER JOIN servicedayopeningtimes sdot "
        "ON sdo.id = sdot.servicedayopeningid "
        "LEFT JOIN openingtimedays otd "
        "ON sdo.dayid = otd.id "
        f"WHERE sdo.serviceid = {serviceid}"
    )
    c = query_dos_db(sql_command)

    standard_opening_times = StandardOpeningTimes()
    for row in c.fetchall():
        weekday = row[2].lower()
        start = row[3]
        end = row[4]
        open_period = OpenPeriod(start, end)
        standard_opening_times.add_open_period(open_period, weekday)

    c.close()
    return standard_opening_times


def _connect_dos_db() -> None:
    """Creates a new connection to the DoS DB and returns the connection object

    warning: Do not use. Should only be used by query_dos_db() func
    """

    server = environ["DB_SERVER"]
    port = environ["DB_PORT"]
    db_name = environ["DB_NAME"]
    db_schema = environ["DB_SCHEMA"]
    db_user = environ["DB_USER_NAME"]
    db_password = environ["DB_PASSWORD"]

    logger.debug(f"Attempting connection to database '{server}'")
    logger.debug(f"host={server}, port={port}, dbname={db_name}, schema={db_schema} " f"user={db_user}")

    db = psycopg2.connect(
        host=server,
        port=port,
        dbname=db_name,
        user=db_user,
        password=db_password,
        connect_timeout=30,
        options=f"-c search_path=dbo,{db_schema}",
    )

    return db


def query_dos_db(sql_command: str) -> DictCursor:
    """Queries the dos database with given sql command and returns the resulting cursor object"""

    # Check if new connection needed.
    global db_connection
    if db_connection is None or db_connection.closed != 0:
        db_connection = _connect_dos_db()
    else:
        logger.info("Using existing open database connection.")

    logger.info(f"Running SQL command: {sql_command}")
    c = db_connection.cursor(cursor_factory=DictCursor)
    c.execute(sql_command)
    return c


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
    sql_command = f"SELECT {', '.join(db_column_names)} FROM locations WHERE postcode ~* '{pc_regex}'"
    c = query_dos_db(sql_command)
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
