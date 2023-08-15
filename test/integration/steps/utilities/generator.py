from ast import literal_eval
from datetime import datetime
from json import loads
from os import getenv
from random import randrange
from re import fullmatch
from typing import Any

from boto3 import client
from pytz import timezone

from .context import Context
from .utils import invoke_dos_db_handler_lambda

URL = getenv("HTTPS_DOS_INTEGRATION_URL")
DYNAMO_DB_TABLE = getenv("DYNAMO_DB_TABLE")
LAMBDA_CLIENT_FUNCTIONS = client("lambda")
SQS_CLIENT = client("sqs", region_name="eu-west-2")
DYNAMO_CLIENT = client("dynamodb")
S3_CLIENT = client("s3", region_name="eu-west-2")


# Commit new services to DOS
def commit_new_service_to_dos(context: Context) -> str:
    """Commit new services to DoS.

    Args:
        context (Context): Test context object.

    Returns:
        str: The response from the lambda.
    """
    qv = context.generator_data
    query_vars = (
        f"{qv['id']}",
        f"{qv['uid']}",
        f"{qv['name']}",
        f"{qv['odscode']}",
        None,
        "false",
        "",
        "false",
        "false",
        f"{qv['address']}${qv['town']}",
        f"{qv['town']}",
        f"{qv['postcode']}",
        None,
        None,
        f"{qv['publicphone']}",
        None,
        None,
        None,
        f"{qv['web']}",
        None,
        "2022-09-06 11:00:00.000 +0100",
        None,
        "2022-09-06 11:00:00.000 +0100",
        "0",
        None,
        f"{qv['service_type']}",
        None,
        None,
        f"{qv['service_status']}",
        None,
        None,
        "0",
        None,
        None,
    )
    query = (
        "INSERT INTO pathwaysdos.services VALUES "
        "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
        "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id"
    )
    lambda_payload = {"type": "read", "query": query, "query_vars": query_vars}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    data = loads(response)
    data = literal_eval(data)
    return data[0]["id"]


# Generic Opening days and times to DOS
def add_single_opening_day(context: Context) -> None:
    """Add a single opening day to a service in DoS.

    Args:
        context (Context): Test context
    """
    # This is a generic single Monday 9-5 opening time
    service_id = context.service_id
    query = f"INSERT INTO servicedayopenings(serviceid, dayid) VALUES({service_id},1) RETURNING id"
    lambda_payload = {"type": "read", "query": query, "query_vars": None}
    response = loads(invoke_dos_db_handler_lambda(lambda_payload))
    time_id = literal_eval(response)[0]["id"]
    add_single_opening_time(context, time_id)
    if "standard_openings" not in context.generator_data:
        context.generator_data["standard_openings"] = []
    context.generator_data["standard_openings"].append(
        {"day": "Monday", "open": True, "opening_time": "09:00", "closing_time": "17:00"},
    )


def add_single_opening_time(context: Context, time_id: int) -> None:
    """Add a single opening time to a service in DoS.

    Args:
        context (Context): Test context
        time_id (int): The id of the opening day
    """
    query = (
        "INSERT INTO servicedayopeningtimes(starttime, endtime, servicedayopeningid) "
        f"VALUES('09:00:00', '17:00:00', {time_id}) RETURNING id"
    )
    lambda_payload = {"type": "read", "query": query, "query_vars": None}
    invoke_dos_db_handler_lambda(lambda_payload)
    context.change_event["OpeningTimes"].append(
        {
            "AdditionalOpeningDate": "",
            "ClosingTime": "17:00",
            "IsOpen": True,
            "OffsetClosingTime": 780,
            "OffsetOpeningTime": 540,
            "OpeningTime": "09:00",
            "OpeningTimeType": "General",
            "Weekday": "Monday",
        },
    )


def add_single_specified_day(context: Context) -> None:
    """Add a single specified opening day to a service in DoS.

    Args:
        context (Context): Test context
    """
    # This is a generic single specified opening day
    service_id = context.service_id
    query = (
        'INSERT INTO servicespecifiedopeningdates("date", serviceid) '
        f"VALUES('2025-01-02', {service_id}) RETURNING id"
    )
    lambda_payload = {"type": "read", "query": query, "query_vars": None}
    response = loads(invoke_dos_db_handler_lambda(lambda_payload))
    time_id = literal_eval(response)[0]["id"]
    add_single_specified_time(context, time_id)
    if "specified_openings" not in context.generator_data:
        context.generator_data["specified_openings"] = []
    context.generator_data["specified_openings"].append(
        {"date": "Jan 02 2025", "open": True, "opening_time": "09:00", "closing_time": "17:00"},
    )


def add_single_specified_time(context: Context, time_id: str) -> None:
    """Add a single specified opening time to a service in DoS.

    Args:
        context (Context): Test context
        time_id (str): The id of the specified opening date
    """
    query = (
        "INSERT INTO servicespecifiedopeningtimes"
        "(starttime, endtime, isclosed, servicespecifiedopeningdateid)"
        f"VALUES('09:00:00', '17:00:00', false, {time_id}) RETURNING id"
    )
    lambda_payload = {"type": "read", "query": query, "query_vars": None}
    invoke_dos_db_handler_lambda(lambda_payload)
    context.change_event["OpeningTimes"].append(
        {
            "AdditionalOpeningDate": "Jan 02 2025",
            "ClosingTime": "17:00",
            "IsOpen": False,
            "OffsetClosingTime": 780,
            "OffsetOpeningTime": 540,
            "OpeningTime": "09:00",
            "OpeningTimeType": "Additional",
            "Weekday": "",
        },
    )


# Standard opening days with specified times to DOS
def add_standard_openings_to_dos(context: Context) -> None:
    """Add standard opening days to DoS Service in database.

    Args:
        context (dict): Test context
    """
    for day in context.generator_data["standard_openings"]:
        query = (
            "INSERT INTO pathwaysdos.servicedayopenings(serviceid, dayid) VALUES "  # noqa: S608
            f'({int(context.service_id)}, {day_lookup(day["day"])}) RETURNING id'
        )
        lambda_payload = {"type": "read", "query": query, "query_vars": None}
        response = invoke_dos_db_handler_lambda(lambda_payload)
        entry_id = literal_eval(loads(response))[0]["id"]
        day["dos_id"] = entry_id
    for day in context.generator_data["standard_openings"]:
        if day["open"] is True:
            opening_time = day["opening_time"]
            closing_time = day["closing_time"]
            day_id = day["dos_id"]
            query = (
                "INSERT INTO pathwaysdos.servicedayopeningtimes(starttime, endtime, servicedayopeningid) VALUES "  # noqa: S608, E501
                f"('{opening_time}', "
                f"'{closing_time}', "
                f"{int(day_id)}) RETURNING id"
            )
            lambda_payload = {"type": "read", "query": query, "query_vars": None}
            invoke_dos_db_handler_lambda(lambda_payload)


# Specified opening days with specified times to DOS
def add_specified_openings_to_dos(context: Context) -> Any:
    """Add specified opening days to DoS Service in database.

    Args:
        context (dict): Test context

    Returns:
        Any: Response from database
    """
    for day in context.generator_data["specified_openings"]:
        date = datetime.strptime(day["date"], "%b %d %Y").strftime("%Y-%m-%d")
        query = (
            'INSERT INTO pathwaysdos.servicespecifiedopeningdates("date", serviceid) '
            f"VALUES('{date!s}', {int(context.service_id)}) RETURNING id"
        )
        lambda_payload = {"type": "read", "query": query, "query_vars": None}
        response = invoke_dos_db_handler_lambda(lambda_payload)
        entry_id = literal_eval(loads(response))[0]["id"]
        day["dos_id"] = entry_id
    for day in context.generator_data["specified_openings"]:
        opening_time = day["opening_time"]
        closing_time = day["closing_time"]
        day_id = day["dos_id"]
        closed_status = ""
        if day["open"] is True:
            closed_status = "false"
        else:
            closed_status = "true"
            opening_time = "00:00:00"
            closing_time = "00:00:00"
        query = (
            "INSERT INTO pathwaysdos.servicespecifiedopeningtimes"
            "(starttime, endtime, isclosed, servicespecifiedopeningdateid) VALUES("
            f"'{opening_time}', '{closing_time}', {closed_status}, {int(day_id)}) RETURNING id"
        )
        if "'', '', false" in query:
            msg = "Query has inserted null times into open specified date"
            raise ValueError(msg)
        lambda_payload = {"type": "read", "query": query, "query_vars": None}
        invoke_dos_db_handler_lambda(lambda_payload)
    # TO DO
    return context


# Build change event for test
def build_change_event(context: Context) -> None:
    """Build default change event for test.

    Args:
        context (Context): Test context
    """
    change_event = {
        "ODSCode": context.generator_data["odscode"],
        "Address1": context.generator_data["address"],
        "Address2": None,
        "Address3": None,
        "City": context.generator_data["town"],
        "Postcode": context.generator_data["postcode"],
        "Contacts": build_change_event_contacts(context),
        "County": None,
        "OpeningTimes": build_change_event_opening_times(context),
        "OrganisationName": context.generator_data["name"],
        "OrganisationStatus": "Visible",
        "OrganisationSubType": "Community",
        "OrganisationType": "Pharmacy",
        "OrganisationTypeId": "PHA",
        "UniqueKey": generate_unique_key(),
        "ParentOrganisation": {"ODSCode": "TES", "OrganisationName": "Fake Pharmacy Corporation"},
        "Staff": [],
    }
    context.change_event = change_event


def generate_staff() -> list:
    """Generate staff for change event.

    Returns:
        list: List of staff
    """
    return [
        {
            "Title": "Mr",
            "GivenName": "Dave",
            "FamilyName": "Davies",
            "Role": "Superintendent Pharmacist",
            "Qualification": "Pharmacist",
        },
        {"Title": "Mr", "GivenName": "Tim", "FamilyName": "Timothy", "Role": "Locum Pharmacist", "Qualification": ""},
    ]


def build_change_event_contacts(context: Context) -> list:
    """Build contacts for change event.

    Args:
        context (Context): Test context

    Returns:
        list: List of contacts
    """
    contacts = []
    if context.generator_data["publicphone"] is not None:
        contacts.append(
            {
                "ContactType": "Primary",
                "ContactAvailabilityType": "Office hours",
                "ContactMethodType": "Telephone",
                "ContactValue": context.generator_data["publicphone"],
            },
        )
    if context.generator_data["web"] is not None:
        contacts.append(
            {
                "ContactType": "Primary",
                "ContactAvailabilityType": "Office hours",
                "ContactMethodType": "Website",
                "ContactValue": context.generator_data["web"],
            },
        )
    return contacts


def build_change_event_opening_times(context: Context) -> list:
    """Build opening times for change event.

    Args:
        context (Context): Test context

    Returns:
        list: List of opening times (both standard and specified)
    """
    opening_times = []
    if "standard_openings" in context.generator_data:
        opening_times.extend(
            {
                "AdditionalOpeningDate": "",
                "ClosingTime": days["closing_time"],
                "IsOpen": days["open"],
                "OffsetClosingTime": 780,
                "OffsetOpeningTime": 540,
                "OpeningTime": days["opening_time"],
                "OpeningTimeType": "General",
                "Weekday": days["day"],
            }
            for days in context.generator_data["standard_openings"]
        )
    if "specified_openings" in context.generator_data:
        present = datetime.now(timezone("Europe/London"))
        opening_times.extend(
            {
                "AdditionalOpeningDate": days["date"],
                "ClosingTime": days["closing_time"],
                "IsOpen": days["open"],
                "OffsetClosingTime": 780,
                "OffsetOpeningTime": 540,
                "OpeningTime": days["opening_time"],
                "OpeningTimeType": "Additional",
                "Weekday": "",
            }
            for days in context.generator_data["specified_openings"]
            if datetime.strptime(days["date"], "%b %d %Y").date() > present.date()
        )
    return opening_times


def return_opening_time_dict() -> dict:
    """Returns a dictionary of change event opening times.

    Returns:
        dict: Dictionary of opening times
    """
    return {
        "Weekday": "",
        "OpeningTime": "",
        "ClosingTime": "",
        "OffsetOpeningTime": 0,
        "OffsetClosingTime": 0,
        "OpeningTimeType": "Additional",
        "AdditionalOpeningDate": "",
        "IsOpen": True,
    }


DAYS = {"monday": 1, "tuesday": 2, "wednesday": 3, "thursday": 4, "friday": 5, "saturday": 6, "sunday": 7}


# Other functions
def day_lookup(day: str) -> int:
    """Returns the day of the week as an integer.

    Args:
        day (str): Day of the week

    Returns:
        int: Day of the week as an integer
    """
    return DAYS[day.lower()]


def generate_unique_key(start_number: int = 1, stop_number: int = 1000) -> str:
    """Generates a unique key for the change event.

    Args:
        start_number (int, optional): Start number for randomiser. Defaults to 1.
        stop_number (int, optional): Stop number for randomiser. Defaults to 1000.

    Returns:
        str: Unique key
    """
    return str(randrange(start=start_number, stop=stop_number, step=1))


def query_standard_opening_builder(
    context: Context,
    service_status: str,
    day: str,
    open_time: str = "09:00",
    close_time: str = "17:00",
) -> Context:
    """Builds a query for standard opening times.

    Args:
        context (Context): Test context
        service_status (str): Open or closed
        day (str): Day of the week
        open_time (str, optional): Opening time for the standard opening. Defaults to "09:00".
        close_time (str, optional): Closing time for the standard opening. Defaults to "17:00".

    Returns:
        Context: Test context
    """

    def add_standard_opening_time(day: str, open_or_closed: bool, open_time: str, close_time: str) -> dict:
        """Adds a standard opening time to the generator data.

        Args:
            day (str): Day of the week
            open_or_closed (bool): Open or closed
            open_time (str): Opening time for the standard opening.
            close_time (str): Closing time for the standard opening.

        Returns:
            dict: Standard opening time
        """
        return {
            "day": day,
            "open": open_or_closed,
            "opening_time": open_time,
            "closing_time": close_time,
        }

    if service_status.lower() == "open":
        times_obj = add_standard_opening_time(day, True, open_time, close_time)
    else:
        times_obj = add_standard_opening_time(day, False, "", "")

    if "standard_openings" not in context.generator_data:
        context.generator_data["standard_openings"] = []
    else:
        # Make sure that a closed statement removes opening statements
        for days in context.generator_data["standard_openings"]:
            if days["day"].lower() == day.lower() and times_obj["open"] != days["open"]:
                context.generator_data["standard_openings"].remove(days)
    context.generator_data["standard_openings"].append(times_obj)
    return context


def query_specified_opening_builder(
    context: Context,
    service_status: str,
    date: str,
    open_time: str = "09:00",
    close_time: str = "17:00",
) -> Context:
    """Adds a specified opening to the generator_data.

    Args:
        context (Context): Test context
        service_status (str): Open or Closed
        date (str): Date in format "Jan 01 2021"
        open_time (str, optional): Opening time for the specified opening. Defaults to "09:00".
        close_time (str, optional): Closing time for the specified opening. Defaults to "17:00".

    Returns:
        Context: Test context
    """

    def add_specified_opening_time(
        date: str,
        open_or_closed: bool,
        open_time: str,
        close_time: str,
    ) -> dict:
        """Sets up the specified opening dictionary.

        Args:
            date (str): Date in format "Jan 01 2021"
            open_or_closed (bool): True for open, False for closed
            open_time (str): Opening time for the specified opening.
            close_time (str): Closing time for the specified opening.

        Returns:
            dict: Specified Opening Time instance dictionary
        """
        return {
            "date": date,
            "open": open_or_closed,
            "opening_time": open_time,
            "closing_time": close_time,
        }

    if service_status.lower() == "open":
        times_obj = add_specified_opening_time(date, True, open_time, close_time)
    else:
        times_obj = add_specified_opening_time(date, False, "", "")
    if "specified_openings" not in context.generator_data:
        context.generator_data["specified_openings"] = []
    else:
        for entry in context.generator_data["specified_openings"]:
            if entry["date"] == date:
                context.generator_data["specified_openings"].remove(entry)
    context.generator_data["specified_openings"].append(times_obj)
    return context


def valid_change_event(context: Context) -> bool:
    """This function checks if the data stored in DoS would pass the change request validation within DoS API Gateway.

    Args:
        context (Context): The context object that contains the data to be validated.

    Returns:
        bool: True if the data is valid, False if not.
    """
    return bool(
        (
            context.website is None
            or fullmatch(
                r"(https?:\/\/)?([a-z\d][a-z\d-]*[a-z\d]\.)+[a-z]{2,}(\/.*)?",
                context.website,
            )
        )
        and (context.phone is None or fullmatch(r"[+0][0-9 ()]{9,}", context.phone)),
    )


def create_palliative_care_entry_dos(context: Context) -> int:
    """This function creates an entry in DOS DB that will flag the service as having palliative care service.

    Args:
        context (Context): The context object that contains the service ID to be flagged.

    Returns:
        int: The ID of the entry in the database.
    """
    srv = context.service_id
    query = f"INSERT INTO pathwaysdos.servicesgsds (serviceid, sdid, sgid) VALUES ({srv}, 14167, 360) RETURNING id"  # noqa: E501,S608
    lambda_payload = {"type": "read", "query": query, "query_vars": None}
    return loads(invoke_dos_db_handler_lambda(lambda_payload))


def create_palliative_care_entry_ce(context: Context) -> None:
    """This function creates an entry in the Change Event containing a palliative care service.

    Args:
        context (Context): The context object that contains the change event to be updated.
    """
    context.change_event["UecServices"] = [
        {
            "ServiceName": "Pharmacy palliative care medication stockholder",
            "ServiceDescription": None,
            "ServiceCode": "SRV0559",
            "Contacts": [],
            "Treatments": [],
            "OpeningTimes": [],
            "AgeRange": [],
        },
    ]


def set_up_palliative_care_in_db() -> None:
    """This function sets up the palliative care symptom discriminator.

    Setup in the symptomdisciminators table and in the symptomgroupsymptomdiscriminators table.
    """
    invoke_dos_db_handler_lambda(
        {
            "type": "insert",
            "query": "INSERT INTO pathwaysdos.symptomdiscriminators (id, description) VALUES (14167, 'Pharmacy Palliative Care Medication Stockholder') ON CONFLICT DO NOTHING RETURNING id",  # noqa: E501
            "query_vars": None,
        },
    )
    invoke_dos_db_handler_lambda(
        {
            "type": "insert",
            "query": "INSERT INTO pathwaysdos.symptomgroupsymptomdiscriminators (id, symptomgroupid, symptomdiscriminatorid) VALUES (10000, 360, 14167) ON CONFLICT DO NOTHING RETURNING id",  # noqa: E501
            "query_vars": None,
        },
    )


def set_up_common_condition_service_types() -> None:
    """This function sets up the common condition service types."""
    invoke_dos_db_handler_lambda(
        {
            "type": "insert",
            "query": """INSERT INTO pathwaysdos.servicetypes (id, "name", nationalranking, searchcapacitystatus, capacitymodel, capacityreset) VALUES(148, 'NHS Community Blood Pressure Check service', '1', true, NULL, 'interval') ON CONFLICT DO NOTHING RETURNING id""",  # noqa: E501
            "query_vars": None,
        },
    )
    invoke_dos_db_handler_lambda(
        {
            "type": "insert",
            "query": """INSERT INTO pathwaysdos.servicetypes (id, "name", nationalranking, searchcapacitystatus, capacitymodel, capacityreset) VALUES(149, 'NHS Community Pharmacy Contraception service', '1', true, NULL, 'interval') ON CONFLICT DO NOTHING RETURNING id""",  # noqa: E501
            "query_vars": None,
        },
    )
