from os import environ
from logging import getLogger
from typing import List, Dict
from datetime import datetime, date, time
from itertools import groupby

import psycopg2

from opening_times import *


logger = getLogger("lambda")
db_connection = None
VALID_SERVICE_TYPES = {13, 131, 132, 134, 137}
VALID_STATUS_ID = 1


class DoSService:
    """Class to represent a DoSService"""

    # These values are which columns are selected from the database and then
    # are passed in as attributes into the DoSService object.
    #
    # example: Put 'postcode' in this list and you can use service.postcode in
    # the object
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

    def __init__(self, db_cursor_row):
        """Sets the attributes of this object to those found in the db row
        Args:
            db_cursor_row (dict): Change Request changes
        """
        for i, attribute_name in enumerate(self.db_columns):
            attribute_value = db_cursor_row[i]
            setattr(self, attribute_name, attribute_value)

        # Do not use these, access them via their corresponding methods
        self._standard_opening_times = None
        self._specififed_opening_times = None

    def __repr__(self) -> str:
        """Returns a string representation of this object"""
        if self.publicname is not None:
            name = self.publicname
        elif self.name is not None:
            name = self.name
        else:
            name = "NO-VALID-NAME"

        return (f"<DoSService: name='{name[0:16]}' id={self.id} uid={self.uid} "
                f"odscode={self.odscode} type={self.typeid} status={self.statusid}>")


    def standard_opening_times(self) -> StandardOpeningTimes:
        """ Retrieves values from db on first call. Returns stored
            values on subsequent calls
        """
        if self._standard_opening_times is None:
            self._standard_opening_times = get_standard_opening_times_from_db(self.id)
        return self._standard_opening_times

    def specififed_opening_times(self) -> List[SpecifiedOpeningTime]:
        """ Retrieves values from db on first call. Returns stored
            values on subsequent calls
        """
        if self._specififed_opening_times is None:
            self._specififed_opening_times = get_specified_opening_times_from_db(self.id)
        return self._specififed_opening_times

def get_matching_dos_services(odscode: str) -> List[DoSService]:
    """Retrieves DoS Services from DoS database

    Args:
        odscode (str): ODScode to match on

    Returns:
        list[DoSService]: List of DoSService objects with matching first 5
        digits of odscode, taken from DoS database
    """

    logger.info(f"Searching for DoS services with ODSCode that matches first "
                f"5 digits of '{odscode}'")

    sql_command = (f"SELECT {', '.join(DoSService.db_columns)} "
                   f"FROM services WHERE odscode LIKE '{odscode[0:5]}%'")
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
        List[SpecifiedOpeningTime]: List of Specified Opening times with matching serviceid
    """

    logger.info(
        f"Searching for specified opening times with serviceid that matches '{service_id}'")

    sql_command = ("SELECT ssod.serviceid, ssod.date, ssot.starttime, "
                   "       ssot.endtime, ssot.isclosed "
                   "FROM servicespecifiedopeningdates ssod "
                   "INNER JOIN servicespecifiedopeningtimes ssot "
                   "ON ssod.serviceid = ssot.servicespecifiedopeningdateid "
                  f"WHERE ssod.serviceid = {service_id}")
    c = query_dos_db(sql_command)

    """sort by date and then by starttime"""
    sorted_list = sorted(c.fetchall(), key=lambda row: (row[1], row[2]))
    specified_opening_time_dict : Dict[datetime,List[OpenPeriod]] = {}
    key:date
    for key, value in groupby(sorted_list, lambda row: (row[1])):
        specified_opening_time_dict[key] = [OpenPeriod(row[2], row[3]) for row in list(value)]
    specified_opening_times = [SpecifiedOpeningTime(
        value, key) for key, value in specified_opening_time_dict.items()]
    c.close()
    return specified_opening_times

def get_standard_opening_times_from_db(serviceid) -> StandardOpeningTimes:

    logger.info(f"Searching for standard opening times with serviceid that "
                f"matches '{serviceid}'")

    sql_command = ( "SELECT sdo.serviceid,  sdo.dayid, otd.name, "
                    "sdot.starttime, sdot.endtime "
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

def _connect_dos_db():
    """ Creates a new connection to the DoS DB and returns the
        connection object

        warning: Do not use. Should only be used by query_dos_db() func
    """

    server = environ["DB_SERVER"]
    port = environ["DB_PORT"]
    db_name = environ["DB_NAME"]
    db_user = environ["DB_USER_NAME"]
    db_password = environ["DB_PASSWORD"]

    logger.info(f"Attempting connection to database '{server}'")
    logger.debug(f"host={server}, port={port}, dbname={db_name}, "
                 f"user={db_user}, password={db_password}")
    db = psycopg2.connect(host=server, port=port, dbname=db_name, 
                          user=db_user, password=db_password, 
                          connect_timeout=30)
    return db

def query_dos_db(sql_command):
    """ Querys the dos database with given sql command and
        returns the resulting cursor object.
    """

    # Check if new connection needed. Or use exisiting.
    global db_connection
    if db_connection is None or db_connection.closed != 0:
        db_connection = _connect_dos_db()
    else:
        logger.info("Using existing open database connection.")

    logger.debug(f"Running SQL command: {sql_command}")
    c = db_connection.cursor()
    c.execute(sql_command)
    return c
