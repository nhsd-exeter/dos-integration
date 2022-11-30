from ast import literal_eval
from json import loads
from os import getenv
from random import randint
from typing import Any, Dict

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
        f"{qv['address']}",
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
    service_id = context.service_id
    query = f"INSERT INTO servicedayopenings(serviceid, dayid) VALUES({service_id},1) RETURNING id"
    lambda_payload = {"type": "read", "query": query, "query_vars": None}
    response = loads(invoke_dos_db_handler_lambda(lambda_payload))
    time_id = literal_eval(response)[0][0]
    add_single_opening_time(context, time_id)


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
    service_id = context.service_id
    query = (
        'INSERT INTO servicespecifiedopeningdates("date", serviceid) '
        f"VALUES('2025-01-02', {service_id}) RETURNING id"
    )
    lambda_payload = {"type": "read", "query": query, "query_vars": None}
    response = loads(invoke_dos_db_handler_lambda(lambda_payload))
    time_id = literal_eval(response)[0][0]
    add_single_specified_time(context, time_id)


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
    for day in context.query["standard_openings"].keys():
        entry_id = randint(750000, 999999)
        query = (
            "INSERT INTO pathwaysdos.servicedayopenings VALUES "
            f"({int(entry_id)}, {int(context.service_id)}, {int(day)}) RETURNING id"
        )
        lambda_payload = {"type": "read", "query": query, "query_vars": None}
        invoke_dos_db_handler_lambda(lambda_payload)
        context.query["standard_openings"][day]["day_id"] = entry_id
    for day in context.query["standard_openings"].keys():
        if context.query["standard_openings"][day]["open"] is True:
            unique_id = randint(1000000, 1500000)
            opening_time = context.query["standard_openings"][day]["opening_time"]
            closing_time = context.query["standard_openings"][day]["closing_time"]
            day_id = context.query["standard_openings"][day]["day_id"]
            query = (
                "INSERT INTO pathwaysdos.servicedayopeningtimes VALUES "
                f"({int(unique_id)}, "
                f"'{opening_time}', "
                f"'{closing_time}', "
                f"{int(day_id)}) RETURNING id"
            )
            lambda_payload = {"type": "read", "query": query, "query_vars": None}
            invoke_dos_db_handler_lambda(lambda_payload)
    return context


# Build change event for test


def build_change_event(context):
    # query_values = {
    #     "id": str(randint(100000, 999999)),
    #     "uid": f"test{str(randint(10000,99999))}",
    #     "name": f"Test Pharmacy {str(randint(100,999))}",
    #     "odscode": ods_code,
    #     "address": f"{str(randint(100,999))} Test Address",
    #     "town": "Test Town",
    #     "postcode": "NG11GS",
    #     "publicphone": "01234567890",
    #     "web": "www.google.com",
    # }
    # This function will convert the query into a valid change event
    change_event = {
        "ODSCode": context.query["odscode"],
        "Address1": context.query["address"],
        "Address2": None,
        "Address3": None,
        "City": context.query["town"],
        "Postcode": context.query["postcode"],
        "Contacts": build_change_event_contacts(context),
        "County": None,
        "OpeningTimes": build_change_event_opening_times(context),
        "OrganisationName": context.query["name"],
        "OrganisationStatus": "Visible",
        "OrganisationSubType": "Community",
        "OrganisationType": "Pharmacy",
        "OrganisationTypeId": "PHA",
    }
    context.change_event = change_event


def build_change_event_contacts(context) -> Dict:
    # This function will build the contacts for the CE
    contacts = []
    if context.query["publicphone"] is not None:
        contacts.append(
            {
                "ContactType": "Primary",
                "ContactAvailabilityType": "Office hours",
                "ContactMethodType": "Telephone",
                "ContactValue": context.query["publicphone"],
            }
        )
    if context.query["web"] is not None:
        contacts.append(
            {
                "ContactType": "Primary",
                "ContactAvailabilityType": "Office hours",
                "ContactMethodType": "Website",
                "ContactValue": context.query["web"],
            }
        )
    return contacts


def build_change_event_opening_times(context) -> Dict:
    # This function will build the opening times for the CE
    return True
