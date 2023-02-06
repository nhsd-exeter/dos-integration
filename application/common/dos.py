from collections import defaultdict
from dataclasses import dataclass, fields
from itertools import groupby
from json import dumps
from typing import Dict, Iterable, List, Optional, Set, Union

from aws_lambda_powertools.logging import Logger
from psycopg2.extensions import connection

from .constants import (
    DENTIST_ORG_TYPE_ID,
    DOS_PALLIATIVE_CARE_SYMPTOM_DISCRIMINATOR,
    DOS_PALLIATIVE_CARE_SYMPTOM_GROUP,
    PHARMACY_ORG_TYPE_ID,
    PHARMACY_SERVICE_TYPE_IDS,
)
from .dos_db_connection import connect_to_dos_db_replica, query_dos_db
from .dos_location import DoSLocation
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
    town: str
    postcode: str
    web: str
    typeid: int
    statusid: int
    publicphone: str
    publicname: str
    servicename: str
    easting: int
    northing: int
    latitude: float
    longitude: float

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

        self.standard_opening_times = None
        self.specified_opening_times = None
        self.palliative_care = False

    def __repr__(self) -> str:
        """Returns a string representation of this object"""
        if self.publicname is not None:
            name = self.publicname
        elif self.name is not None:
            name = self.name
        else:
            name = "NO-VALID-NAME"

        return (
            f"<DoSService: name='{name[:16]}' id={self.id} uid={self.uid} "
            f"odscode={self.odscode} type={self.typeid} status={self.statusid}>"
        )

    def normal_postcode(self) -> str:
        return self.postcode.replace(" ", "").upper()

    def any_generic_bankholiday_open_periods(self) -> bool:
        return len(self.standard_opening_times.generic_bankholiday) > 0


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
        named_args = {"ODS": f"{odscode[:5]}%"}
    elif org_type_id == DENTIST_ORG_TYPE_ID:
        conditions = "odscode = %(ODS)s or odscode LIKE %(ODS7)s"
        named_args = {"ODS": f"{odscode[0] + odscode[2:]}", "ODS7": f"{odscode[:7]}%"}
    else:
        conditions = "odscode = %(ODS)s"
        named_args = {"ODS": f"{odscode}%"}

    sql_query = (  # nosec - Safe as conditional is configurable but variables is inputed to psycopg2 as variables
        "SELECT s.id, uid, s.name, odscode, address, postcode, web, typeid,"
        "statusid, publicphone, publicname, st.name servicename"
        " FROM services s LEFT JOIN servicetypes st ON s.typeid = st.id"
        f" WHERE {conditions}"
    )
    with connect_to_dos_db_replica() as connection:
        cursor = query_dos_db(connection=connection, query=sql_query, vars=named_args)
        # Create list of DoSService objects from returned rows
        services = [DoSService(row) for row in cursor.fetchall()]
        cursor.close()
        # Connection closed by context manager
    return services


def get_dos_locations(postcode: Union[str, None] = None, try_cache: bool = True) -> List[DoSLocation]:
    logger.info(f"Searching for DoS locations with postcode of '{postcode}'")
    norm_pc = postcode.replace(" ", "").upper()
    global dos_location_cache
    if try_cache and norm_pc in dos_location_cache:
        logger.info(f"Postcode {norm_pc} location/s found in local cache.")
        return dos_location_cache[norm_pc]

    # Search for any variation of whitespace in postcode
    postcode_variations = [norm_pc] + [f"{norm_pc[:i]} {norm_pc[i:]}" for i in range(1, len(norm_pc))]
    db_column_names = [f.name for f in fields(DoSLocation)]
    sql_command = f"SELECT {', '.join(db_column_names)} FROM locations WHERE postcode IN %(pc_variations)s"
    with connect_to_dos_db_replica() as connection:
        cursor = query_dos_db(
            connection=connection, query=sql_command, vars={"pc_variations": tuple(postcode_variations)}
        )
        dos_locations = [DoSLocation(**row) for row in cursor.fetchall()]
        cursor.close()
    dos_location_cache[norm_pc] = dos_locations
    logger.debug(f"Postcode location/s for {norm_pc} added to local cache.")

    return dos_locations


def get_all_valid_dos_postcodes() -> Set[str]:
    """Gets all the valid DoS postcodes that are found in the locations table.
    Returns: A set of normalised postcodes as strings"""
    logger.info("Collecting all valid postcodes from DoS DB")
    sql_command = "SELECT postcode FROM locations"
    with connect_to_dos_db_replica() as connection:
        cursor = query_dos_db(connection=connection, query=sql_command)
        postcodes = set(row["postcode"].replace(" ", "").upper() for row in cursor.fetchall())
        cursor.close()
    logger.info(f"Found {len(postcodes)} unique postcodes from DoS DB.")
    return postcodes


def get_valid_dos_location(postcode: str) -> Optional[DoSLocation]:
    """Gets the valid DoS location for the given postcode.

    Args:
        postcode (str): The postcode to search for.

    Returns:
        Optional[DoSLocation]: The valid DoS location for the given postcode or None if no valid location is found.
    """
    dos_locations = [loc for loc in get_dos_locations(postcode) if loc.is_valid()]
    return dos_locations[0] if dos_locations else None


def get_services_from_db(typeids: Iterable) -> List[DoSService]:
    """VUNERABLE TO SQL INJECTION: DO NOT USE IN LAMBDA"""
    # Find base services
    sql_query = (  # nosec - Not for use within lambda
        "SELECT s.id, uid, s.name, odscode, address, postcode, web, typeid, "
        "statusid, publicphone, publicname, st.name servicename "
        "FROM services s LEFT JOIN servicetypes st ON s.typeid = st.id "
        f"WHERE typeid IN ({','.join(map(str, typeids))}) "
        f"AND statusid = 1 AND odscode IS NOT NULL"
    )
    with connect_to_dos_db_replica() as connection:
        cursor = query_dos_db(connection=connection, query=sql_query)
        services = [DoSService(row) for row in cursor.fetchall()]
        cursor.close()
        service_id_strings = set(str(s.id) for s in services)

        # Collect and apply all std open times to services
        sql_query = (  # nosec - Not for use within lambda
            "SELECT sdo.serviceid, sdo.dayid, otd.name, sdot.starttime, sdot.endtime "
            "FROM servicedayopenings sdo "
            "INNER JOIN servicedayopeningtimes sdot "
            "ON sdo.id = sdot.servicedayopeningid "
            "LEFT JOIN openingtimedays otd "
            "ON sdo.dayid = otd.id "
            f"WHERE sdo.serviceid IN ({','.join(service_id_strings)})"
        )
        cursor = query_dos_db(connection=connection, query=sql_query)
        std_open_times = db_rows_to_std_open_times_map([db_row for db_row in cursor.fetchall()])
        for service in services:
            service.standard_opening_times = std_open_times.get(service.id, StandardOpeningTimes())
        cursor.close()

        # Collect and apply all spec open times to services
        sql_query = (  # nosec - Not for use within lambda
            "SELECT ssod.serviceid, ssod.date, ssot.starttime, ssot.endtime, ssot.isclosed "
            "FROM servicespecifiedopeningdates ssod "
            "INNER JOIN servicespecifiedopeningtimes ssot "
            "ON ssod.id = ssot.servicespecifiedopeningdateid "
            f"WHERE ssod.serviceid IN ({','.join(service_id_strings)})"
        )
        cursor = query_dos_db(connection=connection, query=sql_query)
        spec_open_times = db_rows_to_spec_open_times_map([row for row in cursor.fetchall()])
        for service in services:
            service.specified_opening_times = spec_open_times.get(service.id, [])
        cursor.close()

    return services


def get_specified_opening_times_from_db(connection: connection, service_id: int) -> List[SpecifiedOpeningTime]:
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
        "WHERE ssod.serviceid = %(SERVICE_ID)s"
    )
    named_args = {"SERVICE_ID": service_id}
    cursor = query_dos_db(connection=connection, query=sql_query, vars=named_args)
    specified_opening_times = db_rows_to_spec_open_times(cursor.fetchall())
    cursor.close()
    return specified_opening_times


def get_standard_opening_times_from_db(connection: connection, service_id: int) -> StandardOpeningTimes:
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
        "WHERE sdo.serviceid = %(SERVICE_ID)s"
    )
    named_args = {"SERVICE_ID": service_id}
    cursor = query_dos_db(connection=connection, query=sql_command, vars=named_args)
    standard_opening_times = db_rows_to_std_open_times(cursor.fetchall())
    cursor.close()
    return standard_opening_times


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


def has_palliative_care(service: DoSService, connection: connection) -> bool:
    """Checks if a service has palliative care

    Args:
        service: The service to check
        connection: The database connection to use

    Returns:
        True if the service has palliative care, False otherwise
    """
    if service.typeid in PHARMACY_SERVICE_TYPE_IDS:
        sql_command = """SELECT sgsds.id as z_code from servicesgsds sgsds
            WHERE sgsds.serviceid = %(SERVICE_ID)s
            AND sgsds.sgid = %(PALIATIVE_CARE_SYMPTOM_GROUP)s
            AND sgsds.sdid  = %(PALIATIVE_CARE_SYMPTOM_DESCRIMINATOR)s
            """
        named_args = {
            "SERVICE_ID": service.id,
            "PALIATIVE_CARE_SYMPTOM_GROUP": DOS_PALLIATIVE_CARE_SYMPTOM_GROUP,
            "PALIATIVE_CARE_SYMPTOM_DESCRIMINATOR": DOS_PALLIATIVE_CARE_SYMPTOM_DISCRIMINATOR,
        }
        cursor = query_dos_db(connection=connection, query=sql_command, vars=named_args)
        cursor.fetchall()
        return cursor.rowcount != 0
    return False
