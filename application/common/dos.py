from dataclasses import dataclass, fields
from itertools import groupby
from typing import Set, List, Union, Iterable, Dict
from collections import defaultdict

from aws_lambda_powertools import Logger

from common.constants import DENTIST_ORG_TYPE_ID, PHARMACY_ORG_TYPE_ID
from .dos_db_connection import query_dos_db
from .opening_times import OpenPeriod, SpecifiedOpeningTime, StandardOpeningTimes

VALID_STATUS_ID = 1
logger = Logger(child=True)
dos_location_cache = {}


@dataclass
class DoSService:
    """Class to represent a DoS Service, field names are equal to equivalent db column names."""

    id: int
    uid: int
    name: str
    odscode: str
    address: str
    postcode: str
    web: str
    typeid: int
    statusid: int
    publicphone: str
    publicname: str
    servicename: str

    @staticmethod
    def field_names() -> List[str]:
        return [f.name for f in fields(DoSService)]

    def __init__(self, db_cursor_row: dict) -> None:
        """Sets the attributes of this object to those found in the db row
        Args:
            db_cursor_row (dict): row from db as key/val pairs
        """

        for row_key, row_value in db_cursor_row.items():
            setattr(self, row_key, row_value)

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
    logger.info(f"Searching for '{org_type_id}' DoS services with ODSCode that matches '{odscode}'")

    if org_type_id == PHARMACY_ORG_TYPE_ID:
        conditions = "odscode LIKE %(ODS)s"
        named_args = {"ODS": f"{odscode[0:5]}%"}
    elif org_type_id == DENTIST_ORG_TYPE_ID:
        conditions = "odscode = %(ODS)s or odscode LIKE %(ODS7)s"
        named_args = {"ODS": f"{odscode[0] + odscode[2:]}", "ODS7": f"{odscode[0:7]}%"}
    else:
        conditions = "odscode = %(ODS)s"
        named_args = {"ODS": f"{odscode}%"}

    sql_query = (
        "SELECT s.id, uid, s.name, odscode, address, postcode, web, typeid,"
        "statusid, publicphone, publicname, st.name servicename"
        " FROM services s LEFT JOIN servicetypes st ON s.typeid = st.id"
        f" WHERE {conditions}"
    )

    c = query_dos_db(query=sql_query, vars=named_args)

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

    sql_query = (
        "SELECT ssod.serviceid, ssod.date, ssot.starttime, ssot.endtime, ssot.isclosed "
        "FROM servicespecifiedopeningdates ssod "
        "INNER JOIN servicespecifiedopeningtimes ssot "
        "ON ssod.id = ssot.servicespecifiedopeningdateid "
        "WHERE ssod.serviceid = %(service_id)s"
    )
    named_args = {"service_id": service_id}
    c = query_dos_db(sql_query, named_args)
    specified_opening_times = db_rows_to_spec_open_times(c.fetchall())
    c.close()
    return specified_opening_times


def get_standard_opening_times_from_db(service_id: int) -> StandardOpeningTimes:
    """Retrieves standard opening times from DoS database. If ther service id does not even match any service this
    function will still return a blank StandardOpeningTime with no opening periods."""

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
    standard_opening_times = db_rows_to_std_open_times(c.fetchall())
    c.close()
    return standard_opening_times


def get_dos_locations(postcode: Union[str, None] = None) -> List[DoSLocation]:
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


def get_all_valid_dos_postcodes() -> Set[str]:
    """Gets all the valid DoS postcodes that are found in the locations table.
    Returns: A set of normalised postcodes as strings"""
    logger.info("Collecting all valid postcodes from DoS DB")
    sql_command = "SELECT postcode FROM locations"
    c = query_dos_db(sql_command)
    postcodes = set(row["postcode"].replace(" ", "").upper() for row in c.fetchall())
    logger.info(f"Found {len(postcodes)} unique postcodes from DoS DB.")
    return postcodes


def get_valid_dos_postcode(postcode: str) -> Union[str, None]:
    """Finds the valid DoS formatted version of the given postcode. Or None if not a valid DoS postcode"""
    dos_locations = [loc for loc in get_dos_locations(postcode) if loc.is_valid()]
    if len(dos_locations) == 0:
        return None
    return dos_locations[0].postcode


def get_services_from_db(typeids: Iterable) -> List[DoSService]:

    # Find base services
    sql_query = (
        "SELECT s.id, uid, s.name, odscode, address, postcode, web, typeid, "
        "statusid, publicphone, publicname, st.name servicename "
        "FROM services s LEFT JOIN servicetypes st ON s.typeid = st.id "
        f"WHERE typeid IN ({','.join(map(str, typeids))}) "
        f"AND statusid = 1 AND odscode IS NOT NULL"
    )

    c = query_dos_db(sql_query)
    services = [DoSService(row) for row in c.fetchall()]
    c.close()
    service_id_strings = set(str(s.id) for s in services)

    # Collect and apply all std open times to services
    sql_query = (
        "SELECT sdo.serviceid, sdo.dayid, otd.name, sdot.starttime, sdot.endtime "
        "FROM servicedayopenings sdo "
        "INNER JOIN servicedayopeningtimes sdot "
        "ON sdo.id = sdot.servicedayopeningid "
        "LEFT JOIN openingtimedays otd "
        "ON sdo.dayid = otd.id "
        f"WHERE sdo.serviceid IN ({','.join(service_id_strings)})"
    )
    c = query_dos_db(sql_query)
    std_open_times = db_rows_to_std_open_times_map([db_row for db_row in c.fetchall()])
    for service in services:
        service._standard_opening_times = std_open_times.get(service.id, StandardOpeningTimes())
    c.close()

    # Collect and apply all spec open times to services
    sql_query = (
        "SELECT ssod.serviceid, ssod.date, ssot.starttime, ssot.endtime, ssot.isclosed "
        "FROM servicespecifiedopeningdates ssod "
        "INNER JOIN servicespecifiedopeningtimes ssot "
        "ON ssod.id = ssot.servicespecifiedopeningdateid "
        f"WHERE ssod.serviceid IN ({','.join(service_id_strings)})"
    )
    c = query_dos_db(sql_query)
    spec_open_times = db_rows_to_spec_open_times_map([row for row in c.fetchall()])
    for service in services:
        service._specified_opening_times = spec_open_times.get(service.id, [])
    c.close()

    return services


def db_rows_to_spec_open_times(db_rows: Iterable[dict]) -> List[SpecifiedOpeningTime]:
    """Turns a set of dos database rows into a list of SpecifiedOpenTime objects
    note: The rows must to be for the same service
    """
    specified_opening_times = []
    date_sorted_rows = sorted(db_rows, key=lambda row: (row["date"], row["starttime"]))
    for date, db_rows in groupby(date_sorted_rows, lambda row: row["date"]):
        is_open = True
        open_periods = []
        for row in list(db_rows):
            if row["isclosed"] is True:
                is_open = False
            else:
                open_periods.append(OpenPeriod(row["starttime"], row["endtime"]))
        specified_opening_times.append(SpecifiedOpeningTime(open_periods, date, is_open))

    return specified_opening_times


def db_rows_to_spec_open_times_map(db_rows: Iterable[dict]) -> Dict[str, List[SpecifiedOpeningTime]]:
    """Turns a set of dos database rows (from multiple services) into lists of SpecifiedOpenTime objects
    which are sorted into a dictionary where the key is the service id of the service those SpecifiedOpenTime
    objects correspond to.
    """
    serviceid_dbrows_map = defaultdict(list)
    for db_row in db_rows:
        serviceid_dbrows_map[db_row["serviceid"]].append(db_row)

    serviceid_specopentimes_map = {}
    for service_id, db_rows in serviceid_dbrows_map.items():
        serviceid_specopentimes_map[service_id] = db_rows_to_spec_open_times(db_rows)

    return serviceid_specopentimes_map


def db_rows_to_std_open_times(db_rows: Iterable[dict]) -> StandardOpeningTimes:
    """Turns a set of dos database rows into a StandardOpeningTime object
    note: The rows must be for the same service
    """
    standard_opening_times = StandardOpeningTimes()
    for row in db_rows:
        weekday = row["name"].lower()
        start = row["starttime"]
        end = row["endtime"]
        open_period = OpenPeriod(start, end)
        standard_opening_times.add_open_period(open_period, weekday)
    return standard_opening_times


def db_rows_to_std_open_times_map(db_rows: Iterable[dict]) -> Dict[str, StandardOpeningTimes]:
    """Turns a set of dos database rows (from multiple services) into StandardOpeningTime objects
    which are sorted into a dictionary where the key is the service id of the service those StandardOpeningTime
    objects correspond to.
    """
    serviceid_dbrows_map = defaultdict(list)
    for db_row in db_rows:
        serviceid_dbrows_map[db_row["serviceid"]].append(db_row)

    serviceid_stdopentimes_map = {}
    for service_id, db_rows in serviceid_dbrows_map.items():
        serviceid_stdopentimes_map[service_id] = db_rows_to_std_open_times(db_rows)

    return serviceid_stdopentimes_map
