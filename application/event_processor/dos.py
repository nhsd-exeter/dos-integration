from os import environ
from logging import getLogger
from datetime import datetime
import random

import boto3
import psycopg2

from nhs import NHSEntity

log = getLogger("lambda")

sec_manager = boto3.client("secretsmanager", region_name="eu-west-2")

valid_service_types = {13, 131, 132, 134, 137}
valid_status_id = 1


class DoSService:

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

        # Sets the attributes of this object to those found in the db row
        for i, attribute_name in enumerate(self.db_columns):
            attrbute_value = db_cursor_row[i]
            setattr(self, attribute_name, attrbute_value)

    def __repr__(self):
        if self.publicname is not None:
            name = self.publicname
        elif self.name is not None:
            name = self.name
        else:
            name = "NO-VALID-NAME"

        return f"<uid={self.uid} ods={self.odscode} type={self.typeid} " f"status={self.statusid} name='{name}'>"

    def ods5(self):
        """First 5 digits of odscode"""
        return self.odscode[0:5]

    def get_changes(self, nhs_entity) -> dict:
        """Returns a dict of the changes that are required to get
        the service inline with the given nhs_entity
        """

        changes = {}

        # WEBSITE
        if self.web != nhs_entity.Website:
            changes["Website"] = nhs_entity.Website

        # TODO in future tickets: Add in checks for the rest of the
        # possible changes

        return changes


def dummy_dos_service():
    """Creates a DoSService Object with random data for the unit testing"""
    test_data = []
    for col in DoSService.db_columns:
        random_str = "".join(random.choices("ABCDEFGHIJKLM", k=8))
        test_data.append(random_str)
    return DoSService(test_data)


def get_matching_dos_services(odscode):
    """Retrieves DoS Services from DoS database

    input:  ODSCode

    output: List of DoSService objects with matching first 5 digits

            of ODSCode, taken from DoS database
    """

    log.info(f"Searching for DoS services with ODSCode that matches first " f" 5 digits of '{odscode}'")

    # Check size of ODSCode, fail if shorter than 5, warn if longer
    if len(odscode) < 5:
        raise Exception(f"ODSCode '{odscode}' is too short.")
    if len(odscode) > 5:
        log.warn(f"ODSCode '{odscode}' is longer than exptected 5 characters")

    # Get DB details from env variables
    server = environ["DB_SERVER"]
    port = environ["DB_PORT"]
    db_name = environ["DB_NAME"]
    db_user = environ["DB_USER_NAME"]
    secret_name = environ["DB_SECRET_NAME"]

    # Collect the DB password from AWS secrets manager
    secret_response = sec_manager.get_secret_value(SecretId=secret_name)
    password = secret_response["SecretString"]

    # Connect to Database
    log.info(f"Attempting connection to database '{server}'")
    db = psycopg2.connect(host=server, port=port, dbname=db_name, user=db_user, password=password)

    # Create and run SQL Command with inputted odscode SELECTING columns
    # defined at top of file and using the 'LIKE' command to match first
    # 5 digits of ODSCode
    sql_command = (
        f"SELECT {', '.join(DoSService.db_columns)} " f"FROM services " f"WHERE odscode LIKE '{odscode[0:5]}%'"
    )
    log.info(f"Created SQL command to run: {sql_command}")
    c = db.cursor()
    c.execute(sql_command)

    # Create list of DoSService objects from returned rows
    services = [DoSService(row) for row in c.fetchall()]

    return services
