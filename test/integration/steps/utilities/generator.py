from ast import literal_eval
from json import loads
from os import getenv
from random import randrange
from typing import Any, Dict
from datetime import datetime
from re import fullmatch

from boto3 import client

from .utils import invoke_dos_db_handler_lambda

URL = getenv("URL")
DYNAMO_DB_TABLE = getenv("DYNAMO_DB_TABLE")
LAMBDA_CLIENT_FUNCTIONS = client("lambda")
SQS_CLIENT = client("sqs", region_name="eu-west-2")
DYNAMO_CLIENT = client("dynamodb")
S3_CLIENT = client("s3", region_name="eu-west-2")


# Commit new services to DOS
def commit_new_service_to_dos(qv: Dict) -> Any:
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
        13,
        None,
        None,
        1,
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
    return data[0][0]


# Generic Opening days and times to DOS
def add_single_opening_day(context):
    # This is a generic single Monday 9-5 opening time
    service_id = context.service_id
    query = f"INSERT INTO servicedayopenings(serviceid, dayid) VALUES({service_id},1) RETURNING id"
    lambda_payload = {"type": "read", "query": query, "query_vars": None}
    response = loads(invoke_dos_db_handler_lambda(lambda_payload))
    time_id = literal_eval(response)[0][0]
    add_single_opening_time(context, time_id)
    # standard_openings: [{day: "Monday", open: True, opening_time: "09:00", closing_time: "17:00"}]
    if "standard_openings" not in context.generator_data.keys():
        context.generator_data["standard_openings"] = []
    context.generator_data["standard_openings"].append(
        {"day": "Monday", "open": True, "opening_time": "09:00", "closing_time": "17:00"}
    )


def add_single_opening_time(context, time_id):
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
        }
    )


def add_single_specified_day(context):
    # This is a generic single specified opening day
    service_id = context.service_id
    query = (
        'INSERT INTO servicespecifiedopeningdates("date", serviceid) '
        f"VALUES('2025-01-02', {service_id}) RETURNING id"
    )
    lambda_payload = {"type": "read", "query": query, "query_vars": None}
    response = loads(invoke_dos_db_handler_lambda(lambda_payload))
    time_id = literal_eval(response)[0][0]
    add_single_specified_time(context, time_id)
    if "specified_openings" not in context.generator_data.keys():
        context.generator_data["specified_openings"] = []
    context.generator_data["specified_openings"].append(
        {"date": "Jan 02 2025", "open": True, "opening_time": "09:00", "closing_time": "17:00"}
    )


def add_single_specified_time(context, time_id):
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
        }
    )


# Standard opening days with specified times to DOS
def add_standard_openings_to_dos(context: Dict) -> Any:
    for day in context.generator_data["standard_openings"]:
        query = (
            "INSERT INTO pathwaysdos.servicedayopenings(serviceid, dayid) VALUES "
            f'({int(context.service_id)}, {day_lookup(day["day"])}) RETURNING id'
        )
        lambda_payload = {"type": "read", "query": query, "query_vars": None}
        response = invoke_dos_db_handler_lambda(lambda_payload)
        entry_id = literal_eval(loads(response))[0][0]
        day["dos_id"] = entry_id
    for day in context.generator_data["standard_openings"]:
        if day["open"] is True:
            opening_time = day["opening_time"]
            closing_time = day["closing_time"]
            day_id = day["dos_id"]
            query = (
                "INSERT INTO pathwaysdos.servicedayopeningtimes(starttime, endtime, servicedayopeningid) VALUES "
                f"('{opening_time}', "
                f"'{closing_time}', "
                f"{int(day_id)}) RETURNING id"
            )
            lambda_payload = {"type": "read", "query": query, "query_vars": None}
            invoke_dos_db_handler_lambda(lambda_payload)
    return context


# Specified opening days with specified times to DOS
def add_specified_openings_to_dos(context: Dict) -> Any:
    # specified_openings: [{date: "25 Dec 2025", open: True, opening_time: "09:00", closing_time: "17:00"}]
    for day in context.generator_data["specified_openings"]:
        date = datetime.strptime(day["date"], "%b %d %Y").strftime("%Y-%m-%d")
        query = (
            'INSERT INTO pathwaysdos.servicespecifiedopeningdates("date", serviceid) '
            f"VALUES('{str(date)}', {int(context.service_id)}) RETURNING id"
        )
        lambda_payload = {"type": "read", "query": query, "query_vars": None}
        response = invoke_dos_db_handler_lambda(lambda_payload)
        entry_id = literal_eval(loads(response))[0][0]
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
            raise ValueError("Query has inserted null times into open specified date")
        lambda_payload = {"type": "read", "query": query, "query_vars": None}
        invoke_dos_db_handler_lambda(lambda_payload)
    # TO DO
    return context


# Build change event for test
def build_change_event(context):
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
    }
    context.change_event = change_event


def build_change_event_contacts(context) -> list:
    # This function will build the contacts for the CE
    contacts = []
    if context.generator_data["publicphone"] is not None:
        contacts.append(
            {
                "ContactType": "Primary",
                "ContactAvailabilityType": "Office hours",
                "ContactMethodType": "Telephone",
                "ContactValue": context.generator_data["publicphone"],
            }
        )
    if context.generator_data["web"] is not None:
        contacts.append(
            {
                "ContactType": "Primary",
                "ContactAvailabilityType": "Office hours",
                "ContactMethodType": "Website",
                "ContactValue": context.generator_data["web"],
            }
        )
    return contacts


def build_change_event_opening_times(context) -> list:
    opening_times = []
    if "standard_openings" in context.generator_data.keys():
        for days in context.generator_data["standard_openings"]:
            opening_times.append(
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
            )
    if "specified_openings" in context.generator_data.keys():
        present = datetime.now()
        for days in context.generator_data["specified_openings"]:
            if datetime.strptime(days["date"], "%b %d %Y").date() > present.date():
                opening_times.append(
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
                )
    return opening_times


def return_opening_time_dict() -> Dict:
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


# Other functions
def day_lookup(day):
    days = {"monday": 1, "tuesday": 2, "wednesday": 3, "thursday": 4, "friday": 5, "saturday": 6, "sunday": 7}
    return days[day.lower()]


def generate_unique_key(start_number: int = 1, stop_number: int = 1000) -> str:
    return str(randrange(start=start_number, stop=stop_number, step=1))


def query_standard_opening_builder(context, service_status, day, open="09:00", close="17:00"):
    # specified_openings: [{date: "25 Dec 2025", open: True, opening_time: "09:00", closing_time: "17:00"}]
    times_obj = {}
    if service_status.lower() == "open":
        times_obj["day"] = day.lower()
        times_obj["open"] = True
        times_obj["opening_time"] = open
        times_obj["closing_time"] = close
    else:
        times_obj["day"] = day.lower()
        times_obj["open"] = False
        times_obj["opening_time"] = ""
        times_obj["closing_time"] = ""
    if "standard_openings" not in context.generator_data.keys():
        context.generator_data["standard_openings"] = []
    else:
        # Make sure that a closed statement removes opening statements
        for days in context.generator_data["standard_openings"]:
            if days["day"].lower() == day.lower():
                if times_obj["open"] != days["open"]:
                    context.generator_data["standard_openings"].remove(days)
    context.generator_data["standard_openings"].append(times_obj)
    return context


def query_specified_opening_builder(context, service_status, date, open="09:00", close="17:00"):
    times_obj = {}
    if service_status.lower() == "open":
        times_obj["date"] = date
        times_obj["open"] = True
        times_obj["opening_time"] = open
        times_obj["closing_time"] = close
    else:
        times_obj["date"] = date
        times_obj["open"] = False
        times_obj["opening_time"] = ""
        times_obj["closing_time"] = ""
    if "specified_openings" not in context.generator_data.keys():
        context.generator_data["specified_openings"] = []
    else:
        for entry in context.generator_data["specified_openings"]:
            if entry["date"] == date:
                context.generator_data["specified_openings"].remove(entry)
    context.generator_data["specified_openings"].append(times_obj)
    return context


def valid_change_event(context):
    """This function checks if the data stored in DoS would pass the change request
    validation within DoS API Gateway"""
    if context.website is not None and not fullmatch(
        r"(https?:\/\/)?([a-z\d][a-z\d-]*[a-z\d]\.)+[a-z]{2,}(\/.*)?",
        context.website,
    ):
        return False
    if context.phone is not None and not fullmatch(r"[+0][0-9 ()]{9,}", context.phone):
        return False
    return True
