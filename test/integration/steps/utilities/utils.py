from ast import literal_eval
from datetime import datetime, timedelta
from decimal import Decimal
from json import dumps, load, loads
from os import getenv, remove
from random import randint, randrange, sample
from re import sub
from time import sleep, time, time_ns
from typing import Any, Dict, Tuple

from boto3 import client, resource
from boto3.dynamodb.types import TypeDeserializer
from pytz import UTC
from requests import get, post, Response

from .change_event import ChangeEvent
from .constants import SERVICE_TYPES
from .context import Context
from .secrets_manager import get_secret
from .translation import get_service_history_data_key

URL = getenv("URL")
DYNAMO_DB_TABLE = getenv("DYNAMO_DB_TABLE")
LAMBDA_CLIENT_FUNCTIONS = client("lambda")
SQS_CLIENT = client("sqs", region_name="eu-west-2")
DYNAMO_CLIENT = client("dynamodb")
S3_CLIENT = client("s3", region_name="eu-west-2")

PHARMACY_ODS_CODE_LIST = None
DENTIST_ODS_CODE_LIST = None


def process_payload(change_event: ChangeEvent, valid_api_key: bool, correlation_id: str) -> Response:
    api_key = "invalid"
    if valid_api_key:
        api_key = loads(get_secret(getenv("API_KEY_SECRET")))[getenv("NHS_UK_API_KEY")]
    sequence_number = generate_unique_sequence_number(change_event.odscode)
    headers = {
        "x-api-key": api_key,
        "sequence-number": sequence_number,
        "correlation-id": correlation_id,
        "Content-Type": "application/json",
    }
    payload = change_event.get_change_event()
    output = post(url=URL, headers=headers, data=dumps(payload))
    if valid_api_key and output.status_code != 200:
        raise ValueError(f"Unable to process change request payload. Error: {output.text}")
    return output


def process_payload_with_sequence(change_event: ChangeEvent, correlation_id: str, sequence_id: Any) -> Response:
    api_key = loads(get_secret(getenv("API_KEY_SECRET")))[getenv("NHS_UK_API_KEY")]
    headers = {
        "x-api-key": api_key,
        "correlation-id": correlation_id,
        "Content-Type": "application/json",
    }
    if sequence_id is not None:
        headers["sequence-number"] = str(sequence_id)
    payload = change_event.get_change_event()
    output = post(url=URL, headers=headers, data=dumps(payload))
    if output.status_code != 200 and isinstance(sequence_id, int):
        raise ValueError(f"Unable to process change request payload. Error: {output.text}")
    return output


def get_stored_events_from_dynamo_db(odscode: str, sequence_number: Decimal) -> dict:
    resp = DYNAMO_CLIENT.query(
        TableName=DYNAMO_DB_TABLE,
        IndexName="gsi_ods_sequence",
        ProjectionExpression="ODSCode,SequenceNumber",
        ExpressionAttributeValues={
            ":v1": {
                "S": odscode,
            },
            ":v2": {
                "N": str(sequence_number),
            },
        },
        KeyConditionExpression="ODSCode = :v1 and SequenceNumber = :v2",
        Limit=1,
        ScanIndexForward=False,
    )
    if len(resp["Items"]) == 0:
        raise ValueError(f"No event found in dynamodb for ODSCode {odscode} and SequenceNumber {sequence_number}")
    item = resp["Items"][0]
    deserializer = TypeDeserializer()
    deserialized = {k: deserializer.deserialize(v) for k, v in item.items()}
    return deserialized


def get_latest_sequence_id_for_a_given_odscode(odscode: str) -> int:
    """Get latest sequence id for a given odscode from dynamodb"""
    try:
        resp = DYNAMO_CLIENT.query(
            TableName=DYNAMO_DB_TABLE,
            IndexName="gsi_ods_sequence",
            KeyConditionExpression="ODSCode = :odscode",
            ExpressionAttributeValues={
                ":odscode": {"S": odscode},
            },
            Limit=1,
            ScanIndexForward=False,
            ProjectionExpression="ODSCode,SequenceNumber",
        )
        sequence_number = 0
        if resp.get("Count") > 0:
            sequence_number = int(resp.get("Items")[0]["SequenceNumber"]["N"])
    except Exception as err:
        print(f"Unable to get sequence id from dynamodb for a given ODSCode {odscode} {DYNAMO_DB_TABLE} .Error: {err}")
        raise
    return sequence_number


def generate_unique_sequence_number(odscode: str) -> str:
    return str(get_latest_sequence_id_for_a_given_odscode(odscode) + 1)


def generate_random_int(start_number: int = 1, stop_number: int = 1000) -> str:
    return str(randrange(start=start_number, stop=stop_number, step=1))


def get_odscodes_list(lambda_payload: dict) -> list[list[str]]:
    response = invoke_dos_db_handler_lambda(lambda_payload)
    data = loads(response)
    data = literal_eval(data)
    return data


def get_single_service_pharmacy_odscode() -> Dict:
    query = (
        "select left(odscode,5) from services where typeid = 13 AND statusid = 1 "
        "AND odscode IS NOT null AND LENGTH(odscode) > 4 AND NOT address like '%$%' and odscode in ( "
        "select odscode from (SELECT left(odscode,5) as odscode, COUNT(*) AS amount "
        "FROM services GROUP BY left(odscode,5)) as subset where amount = 1 )"
    )
    lambda_payload = {"type": "read", "query": query, "query_vars": None}
    return invoke_dos_db_handler_lambda(lambda_payload)


def get_pharmacy_odscode() -> str:
    response = get_single_service_pharmacy_odscode()
    data = loads(response)
    data = literal_eval(data)
    odscode = sample(tuple(data), 1)[0][0]
    return odscode


def get_single_service_pharmacy() -> str:
    data = 0
    while data != "1":
        ods_code = get_pharmacy_odscode()
        query = f"SELECT count(*) FROM services where odscode like '{ods_code}%'"
        lambda_payload = {"type": "read", "query": query, "query_vars": None}
        response = invoke_dos_db_handler_lambda(lambda_payload)
        data = response[3]
    return ods_code


def get_changes(correlation_id: str) -> list:
    query = "SELECT value from changes where externalref = '%(CID)s'"
    query_vars = {"CID": correlation_id}
    lambda_payload = {"type": "read", "query": query, "query_vars": query_vars}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    data = loads(loads(response))
    return data


def get_locations_table_data(postcode: str) -> list:
    query = (
        "SELECT postaltown, postcode, easting, northing, latitude, longitude "
        "FROM locations WHERE postcode = %(POSTCODE)s"
    )
    query_vars = {"POSTCODE": postcode}
    lambda_payload = {"type": "read", "query": query, "query_vars": query_vars}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    data = loads(loads(response))
    return data


def get_services_table_location_data(service_id: str) -> list:
    query = "SELECT town, postcode, easting, northing, latitude, longitude FROM services WHERE id = %(SERVICE_ID)s"
    query_vars = {"SERVICE_ID": service_id}
    lambda_payload = {"type": "read", "query": query, "query_vars": query_vars}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    data = loads(loads(response))
    return data


def get_service_uid(service_id: str) -> list:
    query = "SELECT uid FROM services WHERE id = %(SERVICE_ID)s"
    query_vars = {"SERVICE_ID": service_id}
    lambda_payload = {"type": "read", "query": query, "query_vars": query_vars}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    data = loads(loads(response))
    return data


def confirm_changes(correlation_id: str) -> list:
    changes_loop_count = 0
    data = []
    while changes_loop_count < 10:
        sleep(30)
        data = get_changes(correlation_id)
        if data != []:
            break
        changes_loop_count += 1
    return data


def get_approver_status(correlation_id: str) -> list[None] | list[Any]:
    query = "SELECT modifiedtimestamp from changes where approvestatus = 'COMPLETE' and externalref = '%(CID)s'"
    query_vars = {"CID": correlation_id}
    lambda_payload = {"type": "read", "query": query, "query_vars": query_vars}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    data = loads(loads(response))
    return data


def confirm_approver_status(
    correlation_id: str, loop_count: int = 12, sleep_between_loops: int = 60
) -> list[None] | list[Any]:
    approver_loop_count = 0
    data = []
    while approver_loop_count < loop_count:
        sleep(sleep_between_loops)
        data = get_approver_status(correlation_id)
        if data != []:
            break
        approver_loop_count += 1
    return data


def get_service_id(odscode: str) -> str:
    data = []
    query = f"SELECT id FROM services WHERE typeid = 13 AND statusid = 1 AND odscode like '{odscode}%' LIMIT 1"
    for _ in range(16):
        lambda_payload = {"type": "read", "query": query, "query_vars": None}
        response = invoke_dos_db_handler_lambda(lambda_payload)
        data = loads(response)
        data = literal_eval(data)
        if data != []:
            break
        sleep(30)
    else:
        raise ValueError("Error!.. Service Id not found")

    return data[0][0]


def create_pending_change_for_service(service_id: str):
    success_status = False
    unique_id = randint(10000, 99999)
    json_obj = {
        "new": {
            "cmstelephoneno": {"changetype": "add", "data": "abcd", "area": "demographic", "previous": "0"},
            "cmsurl": {"changetype": "add", "data": "abcd", "area": "demographic", "previous": ""},
        },
        "initiator": {"userid": "admin", "timestamp": "2022-09-01 13:35:41"},
        "approver": {"userid": "admin", "timestamp": "01-09-2022 13:35:41"},
    }
    query = (
        "INSERT INTO pathwaysdos.changes "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id"
    )
    query_vars = (
        f"66301ABC-D3A4-0B8F-D7F8-F286INT{unique_id}",
        "PENDING",
        "modify",
        "admin",
        "Test Duplicate",
        "DoS Region",
        dumps(json_obj),
        "2022-09-06 11:00:00.000 +0100",
        "admin",
        "2022-09-06 11:00:00.000 +0100",
        "admin",
        str(service_id),
        None,
        None,
        None,
    )
    lambda_payload = {"type": "write", "query": query, "query_vars": query_vars}
    success_status = invoke_dos_db_handler_lambda(lambda_payload)
    return success_status


def check_pending_service_is_rejected(service_id: str):
    query = "SELECT approvestatus FROM changes WHERE serviceid = %(SERVICE_ID)s"
    query_vars = {"SERVICE_ID": service_id}
    lambda_payload = {"type": "read", "query": query, "query_vars": query_vars}
    success_status = invoke_dos_db_handler_lambda(lambda_payload)
    return success_status


def get_service_type_data(organisation_type_id: str) -> list[int]:
    """Get the valid service types for the organisation type id"""
    return SERVICE_TYPES[organisation_type_id]


def get_change_event_demographics(odscode: str, organisation_type_id: str) -> Dict[str, Any]:
    lambda_payload = {
        "type": "change_event_demographics",
        "odscode": odscode,
        "organisation_type_id": organisation_type_id,
    }
    response = invoke_dos_db_handler_lambda(lambda_payload)
    data = loads(response)
    return data


def get_change_event_standard_opening_times(service_id: str) -> Any:
    lambda_payload = {"type": "change_event_standard_opening_times", "service_id": service_id}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    data = loads(response)
    return data


def get_change_event_specified_opening_times(service_id: str) -> Any:
    lambda_payload = {"type": "change_event_specified_opening_times", "service_id": service_id}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    data = loads(response)
    return data


def get_pharmacy_ods_codes(type_id) -> Dict:
    query = "SELECT LEFT(odscode, 5) FROM services WHERE typeid = %(TYPE_ID)s AND statusid = 1 AND odscode IS NOT NULL"
    query_vars = {"TYPE_ID": type_id}
    lambda_payload = {"type": "read", "query": query, "query_vars": query_vars}
    return invoke_dos_db_handler_lambda(lambda_payload)


def get_odscode_with_contact_data() -> str:
    response = get_pharmacy_ods_codes(13)
    data = loads(response)
    data = literal_eval(data)
    odscode = sample(data, 1)[0][0]
    return odscode


def invoke_dos_db_handler_lambda(lambda_payload: dict) -> Any:
    response_status = False
    response = None
    retries = 0
    while response_status is False:
        response: Any = LAMBDA_CLIENT_FUNCTIONS.invoke(
            FunctionName=getenv("DOS_DB_HANDLER"),
            InvocationType="RequestResponse",
            Payload=dumps(lambda_payload),
        )
        response_payload = response["Payload"].read().decode("utf-8")
        if "errorMessage" not in response_payload:
            return response_payload

        if retries > 6:
            raise ValueError(f"Unable to run test db checker lambda successfully after {retries} retries")
        retries += 1
        sleep(10)


def get_service_table_field(service_id: str, field_name: str) -> Any:
    query = f"SELECT {field_name} FROM services WHERE id = %(SERVICE_ID)s"
    query_vars = {"SERVICE_ID": service_id}
    lambda_payload = {"type": "read", "query": query, "query_vars": query_vars}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    data = loads(loads(response))
    return data[0][0]


def wait_for_service_update(service_id: str) -> Any:
    """Wait for the service to be updated by checking modifiedtime"""
    for _ in range(12):
        sleep(10)
        updated_date_time_str: str = get_service_table_field(service_id, "modifiedtime")
        updated_date_time = datetime.strptime(updated_date_time_str, "%Y-%m-%d %H:%M:%S%z")
        updated_date_time = updated_date_time.replace(tzinfo=UTC)
        two_mins_ago = datetime.now() - timedelta(minutes=2)
        two_mins_ago = two_mins_ago.replace(tzinfo=UTC)
        if updated_date_time > two_mins_ago:
            break
    else:
        raise ValueError(f"Service not updated, service_id: {service_id}")


def service_not_updated(service_id: str):
    """Assert Service not updated in last 2 mins"""
    sleep(60)
    two_mins_ago = datetime.now() - timedelta(minutes=2)
    two_mins_ago = two_mins_ago.replace(tzinfo=UTC)
    updated_date_time_str: str = get_service_table_field(service_id, "modifiedtime")
    updated_date_time = datetime.strptime(updated_date_time_str, "%Y-%m-%d %H:%M:%S%z")
    updated_date_time = updated_date_time.replace(tzinfo=UTC)
    two_mins_ago = datetime.now() - timedelta(minutes=2)
    two_mins_ago = two_mins_ago.replace(tzinfo=UTC)
    assert updated_date_time < two_mins_ago, f"Service updated unexpectantly, service_id: {service_id}"


def get_expected_data(context: Context, changed_data_name: str) -> Any:
    """Get the previous data from the context"""
    match changed_data_name.lower():
        case "phone_no" | "phone" | "public_phone" | "publicphone":
            changed_data = context.change_event.phone
        case "website" | "web":
            changed_data = context.change_event.website
        case "address":
            changed_data = get_address_string(context.change_event)
        case "postcode":
            changed_data = context.change_event.postcode
        case _:
            raise ValueError(f"Error!.. Input parameter '{changed_data_name}' not compatible")
    return changed_data


def get_address_string(change_event: ChangeEvent) -> str:
    address_lines = [
        line
        for line in [
            change_event.address_line_1,
            change_event.address_line_2,
            change_event.address_line_3,
            change_event.city,
            change_event.county,
        ]
        if isinstance(line, str) and line.strip() != ""
    ]
    address = "$".join(address_lines)
    address = sub(r"[A-Za-z]+('[A-Za-z]+)?", lambda word: word.group(0).capitalize(), address)
    address = address.replace("'", "")
    address = address.replace("&", "and")
    return address


def check_service_history(
    service_id: str, plain_english_field_name: str, expected_data: Any, previous_data: Any
) -> None:
    """Check the service history for the expected data and previous data is removed"""
    service_history = get_service_history(service_id)
    first_key_in_service_history = list(service_history.keys())[0]
    changes = service_history[first_key_in_service_history]["new"]
    change_key = get_service_history_data_key(plain_english_field_name)
    if change_key not in changes:
        raise ValueError(f"DoS Change key '{change_key}' not found in latest service history entry")

    assert (
        expected_data == changes[change_key]["data"]
    ), f"Expected data: {expected_data}, Expected data type: {type(expected_data)}, Actual data: {changes[change_key]['data']}"  # noqa

    if "previous" in changes[change_key]:
        if previous_data not in ["unknown", ""]:
            (
                changes[change_key]["previous"] == str(previous_data),
                f"Expected previous data: {previous_data}, Actual data: {changes[change_key]}",
            )
        elif previous_data == "":
            assert (
                changes[change_key]["previous"] is None
            ), f"Expected previous data: {previous_data}, Actual data: {changes[change_key]}"
        else:
            raise ValueError(f"Input parameter '{previous_data}' not compatible")


def service_history_negative_check(service_id: str):
    service_history = get_service_history(service_id)
    if service_history == []:
        return "Not Updated"
    else:
        first_key_in_service_history = list(service_history.keys())[0]
        if check_recent_event(first_key_in_service_history) is False:
            return "Not Updated"
        else:
            return "Updated"


def check_service_history_change_type(service_id: str, change_type: str):
    service_history = get_service_history(service_id)
    first_key_in_service_history = list(service_history.keys())[0]
    change_status = service_history[first_key_in_service_history]["new"][
        list(service_history[first_key_in_service_history]["new"].keys())[0]
    ]["changetype"]
    if check_recent_event(first_key_in_service_history):
        if change_status == change_type:
            return "Change type matches"
        elif change_type == "modify" and change_status == "add":
            return "Change type matches"
        else:
            return "Change type does not match"
    else:
        return "No changes have been made"


def get_service_history_specified_opening_times(service_id: str) -> dict:
    """This function grabs the latest cmsopentimespecified object for a service id and returns it"""
    service_history = get_service_history(service_id)
    specified_open_times = service_history[list(service_history.keys())[0]]["new"]["cmsopentimespecified"]
    return specified_open_times


def get_service_history_standard_opening_times(service_id: str):
    """This function grabs the latest standard opening times changes from service history"""
    service_history = get_service_history(service_id)
    standard_opening_times_from_service_history = []
    for entry in service_history[list(service_history.keys())[0]]["new"]:
        if entry.endswith("day"):
            standard_opening_times_from_service_history.append(
                {entry: service_history[list(service_history.keys())[0]]["new"][entry]}
            )
    return standard_opening_times_from_service_history


def convert_specified_opening(specified_date, closed_status=False) -> str:
    """Converts opening times from CE format to DOS format

    Args:
        specified_date (dict): Specified opening dates from change event
        closed_status (bool): Closed Status since output string changes if closed
    Returns:
        return_string (str): Converted opening dates/times in dos string format "dd-mm-yyyy-06000-12000"
    """
    months = {
        "Jan": "01",
        "Feb": "02",
        "Mar": "03",
        "Apr": "04",
        "May": "05",
        "Jun": "06",
        "Jul": "07",
        "Aug": "08",
        "Sep": "09",
        "Oct": "10",
        "Nov": "11",
        "Dec": "12",
    }
    split_date = specified_date["AdditionalOpeningDate"].split(" ")
    selected_month = months[split_date[0]]
    if closed_status is False:
        opening_time = time_to_seconds(specified_date["OpeningTime"])
        closing_time = time_to_seconds(specified_date["ClosingTime"])
        return_string = f"{split_date[2]}-{selected_month}-{split_date[1]}-{opening_time}-{closing_time}"
    else:
        return_string = f"{split_date[2]}-{selected_month}-{split_date[1]}-closed"
    return return_string


def convert_standard_opening(standard_times) -> list[dict]:
    """Converts standard opening times from change event to be comparable with service history
    Args:
        standard_times (Dict): Standard Opening times pulled from Change Event
    Returns:
        return_list (List): List of Dicts containing name of the day in cms format and times in seconds
    """
    return_list = []
    for entry in standard_times:
        current_day = entry["Weekday"].lower()
        if entry["IsOpen"] is True:
            opening_time = time_to_seconds(entry["OpeningTime"])
            closing_time = time_to_seconds(entry["ClosingTime"])
            return_list.append({"name": f"cmsopentime{current_day}", "times": f"{opening_time}-{closing_time}"})
        else:
            return_list.append({"name": f"cmsopentime{current_day}", "times": "closed"})
    return return_list


def assert_standard_openings(change_type, dos_times, ce_times, strict=False) -> int:
    """Function to assert standard opening times changes. Added to remove complexity for sonar

    Args:
        changetype (Str): The type of change being asserted
        dos_times (Dict): The times pulled from DOS
        ce_times (Dict): The times pulled from the change event to compare too
    Returns:
        counter (Int): The amount of assertions made"""
    counter = 0
    valid_change_types = ["add", "modify"]
    for entry in dos_times:
        currentday = list(entry.keys())[0]
        for dates in ce_times:
            if dates["name"] == currentday:
                assert entry[currentday]["data"]["add"][0] == dates["times"], "ERROR: Dates do not match"
                if strict:
                    assert entry[currentday]["changetype"] == change_type, "ERROR: Incorrect changetype"
                else:
                    assert entry[currentday]["changetype"] in valid_change_types, "ERROR: Incorrect changetype"
                if entry[currentday]["changetype"] == "add":
                    assert "remove" not in entry[currentday]["data"], "ERROR: Remove is present in service history"
                elif entry[currentday]["changetype"] == "modify":
                    assert "remove" in entry[currentday]["data"], f"ERROR: Remove is not present for {currentday}"
                counter += 1
    return counter


def assert_standard_closing(dos_times, ce_times) -> int:
    counter = 0
    for entry in ce_times:
        currentday = entry["name"]
        if entry["times"] == "closed":
            for dates in dos_times:
                if currentday == list(dates.keys())[0]:
                    assert dates[currentday]["changetype"] == "delete", "Open when expected closed"
                    assert (
                        "add" not in dates[currentday]["data"]
                    ), "ERROR: Unexpected add field found in service history"
                    counter += 1
    return counter


def add_new_standard_open_day(standard_opening_times: dict) -> dict:
    week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    selected_day = "Monday"
    open_days = [open_day["Weekday"] for open_day in standard_opening_times]
    if len(open_days) == 0:
        raise ValueError("ERROR: No available days to add")
    for days in week:
        if days not in open_days:
            selected_day = days
            break
    standard_opening_times.append(
        {
            "Weekday": selected_day,
            "OpeningTime": "09:00",
            "ClosingTime": "17:00",
            "OpeningTimeType": "General",
            "IsOpen": True,
        }
    )
    return standard_opening_times


def time_to_seconds(time: str):
    times = time.split(":")
    hour_seconds = int(times[0]) * 3600
    minutes_seconds = int(times[1]) * 60
    return str(hour_seconds + minutes_seconds)


def check_recent_event(event_time: str, time_difference=600) -> bool:
    if int(time() - int(event_time)) <= int(time_difference):
        return True
    else:
        return False


def get_service_history(service_id: str) -> Dict[str, Any]:
    data = []
    retrycounter = 0
    while data == [] and retrycounter < 2:
        query = "SELECT history FROM servicehistories WHERE serviceid = %(SERVICE_ID)s"
        query_vars = {"SERVICE_ID": service_id}
        lambda_payload = {"type": "read", "query": query, "query_vars": query_vars}
        response = invoke_dos_db_handler_lambda(lambda_payload)
        data = loads(loads(response))
        retrycounter += 1
        sleep(30)
    if data != []:
        return loads(data[0][0])
    else:
        return data


def check_received_data_in_dos(corr_id: str, search_key: str, search_param: str) -> bool:
    """NOT COMPATIBLE WITH OPENING TIMES CHANGES"""
    response = confirm_changes(corr_id)
    for row in response:
        change_value = dict(loads(row[0]))
        for dos_change_key in change_value["new"]:
            if dos_change_key == search_key and search_param in change_value["new"][dos_change_key]["data"]:
                return True
    return False


def get_specified_opening_times(service_id: str):
    lambda_payload = {"type": "change_event_specified_opening_times", "service_id": service_id}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    data = loads(loads(response))
    return loads(data[0][0])


def add_specified_opening_time(service_id: str, date: str, start_time: str, end_time: str):
    lambda_payload = {
        "type": "add_specified_opening_time",
        "service_id": service_id,
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
    }
    response = invoke_dos_db_handler_lambda(lambda_payload)
    return response[0][0]


def check_contact_delete_in_dos(corr_id: str, search_key: str):
    response = get_changes(corr_id)
    if_value_not_in_string_raise_exception(search_key, str(response))
    row_found = False
    for row in response:
        for k in dict(loads(row[0]))["new"]:
            if k == search_key:
                if dict(loads(row[0]))["new"][k]["changetype"] == "delete":
                    data = dict(loads(row[0]))["new"][k]["data"]
                    if data == "":
                        row_found = True
    if row_found is True:
        return True
    else:
        raise ValueError("Expected a 'delete' on the website but didn't find one")


def check_standard_received_opening_times_time_in_dos(corr_id: str, search_key: str, search_param: str):
    """ONLY COMPATIBLE WITH OPENING TIMES CHANGES"""
    response = get_changes(corr_id)
    if_value_not_in_string_raise_exception(search_key, str(response))
    for row in response:
        for k in dict(loads(row[0]))["new"]:
            if k == search_key:
                time_in_dos = dict(loads(row[0]))["new"][k]["data"]["add"][0]
                if time_in_dos == search_param:
                    return True
                else:
                    raise ValueError("Standard Opening-time time change not found in Dos changes... {response}")


def if_value_not_in_string_raise_exception(value: str, string: str) -> None:
    if value not in str(string):
        raise ValueError(f"{value} not found..")


def time_to_sec(t):
    h, m = map(int, t.split(":"))
    return (h * 3600) + (m * 60)


def generate_correlation_id(suffix=None) -> str:
    name_no_space = getenv("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0].replace(" ", "_")
    run_id = getenv("RUN_ID")
    correlation_id = f"{run_id}_{time_ns()}_{name_no_space}" if suffix is None else f"{run_id}_{time_ns()}_{suffix}"
    correlation_id = (
        correlation_id if len(correlation_id) < 80 else correlation_id[:79]
    )  # DoS API Gateway max reference is 100 characters
    correlation_id = correlation_id.replace("'", "")
    return correlation_id


def re_process_payload(odscode: str, seq_number: str) -> str:
    lambda_payload = {"odscode": odscode, "sequence_number": seq_number}
    response = LAMBDA_CLIENT_FUNCTIONS.invoke(
        FunctionName=getenv("EVENT_REPLAY"),
        InvocationType="RequestResponse",
        Payload=dumps(lambda_payload),
    )
    response_payload = response["Payload"].read().decode("utf-8")
    return response_payload


def random_pharmacy_odscode() -> str:
    global PHARMACY_ODS_CODE_LIST
    if PHARMACY_ODS_CODE_LIST is None:
        PHARMACY_ODS_CODE_LIST = loads(loads(get_pharmacy_ods_codes(13)))
    odscode_list = sample(PHARMACY_ODS_CODE_LIST, 1)[0]
    PHARMACY_ODS_CODE_LIST.remove(odscode_list)
    odscode = odscode_list[0]
    return odscode


def generate_untaken_ods() -> str:
    success = False
    while success is False:
        odscode = str(randint(10000, 99999))
        if check_ods_list(odscode) is True:
            return odscode


def check_ods_list(odscode: str) -> str:
    query = "SELECT LEFT(odscode, 5) FROM services"
    lambda_payload = {"type": "read", "query": query, "query_vars": None}
    ods_list = get_odscodes_list(lambda_payload)
    if odscode not in ods_list:
        return True
    else:
        return False


def random_dentist_odscode() -> str:
    global DENTIST_ODS_CODE_LIST
    if DENTIST_ODS_CODE_LIST is None:
        query = (
            "SELECT odscode FROM services WHERE typeid = 12 "
            "AND statusid = 1 AND odscode IS NOT NULL AND LENGTH(odscode) = 6 AND LEFT(odscode, 1)='V'"
        )
        lambda_payload = {"type": "read", "query": query, "query_vars": None}
        DENTIST_ODS_CODE_LIST = get_odscodes_list(lambda_payload)
    odscode_list = sample(DENTIST_ODS_CODE_LIST, 1)[0]
    DENTIST_ODS_CODE_LIST.remove(odscode_list)
    odscode = odscode_list[0]
    return f"{odscode[0]}{odscode[1:]}"


def remove_opening_days(opening_times, day) -> dict:
    deletions = []
    for count, times in enumerate(opening_times):
        if times["Weekday"] == day:
            deletions.insert(0, count)
    for entries in deletions:
        del opening_times[entries]
    return opening_times


def slack_retry(message: str) -> str:
    slack_channel, slack_oauth = slack_secrets()
    for _ in range(6):
        sleep(60)
        response_value = check_slack(slack_channel, slack_oauth)
        if message in response_value:
            return response_value
    raise ValueError(f"Slack alert message not found, message: {message}")


def slack_secrets() -> Tuple[str, str]:
    slack_secrets = loads(get_secret("uec-dos-int-dev/deployment"))
    return slack_secrets["SLACK_CHANNEL"], slack_secrets["SLACK_OAUTH"]


def check_slack(channel, token) -> str:
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
    }
    current = str(time() - 3600)
    output = get(url=f"https://slack.com/api/conversations.history?channel={channel}&oldest={current}", headers=headers)
    return output.text


def get_sqs_queue_name(queue_type: str) -> str:
    response = ""
    blue_green_environment = getenv("BLUE_GREEN_ENVIRONMENT")
    shared_environment = getenv("SHARED_ENVIRONMENT")
    profile = getenv("PROFILE")
    match queue_type.lower():
        case "changeevent":
            response = SQS_CLIENT.get_queue_url(
                QueueName=f"uec-dos-int-{shared_environment}-change-event-dead-letter-queue.fifo",
            )
        case "updaterequest":
            response = SQS_CLIENT.get_queue_url(
                QueueName=f"uec-dos-int-{profile}-{blue_green_environment}-update-request-dead-letter-queue.fifo",
            )
        case "updaterequestfail":
            response = SQS_CLIENT.get_queue_url(
                QueueName=f"uec-dos-int-{profile}-{blue_green_environment}-update-request-queue.fifo",
            )
        case _:
            raise ValueError("Invalid SQS queue type specified")

    return response["QueueUrl"]


def get_sqs_message_attributes(odscode="FW404") -> dict:
    message_attributes = {
        "correlation_id": {"DataType": "String", "StringValue": f"sqs-injection-id-{randint(0,1000)}"},
        "message_received": {"DataType": "Number", "StringValue": str(randint(1000, 5000))},
        "message_group_id": {"DataType": "Number", "StringValue": str(randint(1000, 5000))},
        "message_deduplication_id": {"DataType": "String", "StringValue": str(randint(1000, 99999))},
        "dynamo_record_id": {"DataType": "String", "StringValue": "78adf177e2cd469318e854e4e8068dd4"},
        "ods_code": {"DataType": "String", "StringValue": odscode},
        "error_msg": {"DataType": "String", "StringValue": "error_message"},
        "error_msg_http_code": {"DataType": "String", "StringValue": "404"},
        "sequence-number": {"DataType": "Number", "StringValue": str(time_ns())},
    }
    return message_attributes


def generate_sqs_body(website) -> dict:
    sqs_body = {
        "reference": "14451_1657015307500997089_//www.test.com]",
        "system": "DoS Integration",
        "message": "DoS Integration CR. correlation-id: 14451_1657015307500997089_//www.test.com]",
        "replace_opening_dates_mode": True,
        "service_id": "22963",
        "changes": {"website": website},
    }
    return sqs_body


def post_ur_sqs():
    queue_url = get_sqs_queue_name("updaterequest")
    sqs_body = generate_sqs_body("https://www.test.com")

    SQS_CLIENT.send_message(
        QueueUrl=queue_url,
        MessageBody=dumps(sqs_body),
        MessageDeduplicationId=str(randint(10000, 99999)),
        MessageGroupId=str(randint(10000, 99999)),
        MessageAttributes=get_sqs_message_attributes(),
    )
    return True


def post_ur_fifo():
    queue_url = get_sqs_queue_name("updaterequestfail")
    sqs_body = generate_sqs_body("abc@def.com")

    SQS_CLIENT.send_message(
        QueueUrl=queue_url,
        MessageBody=dumps(sqs_body),
        MessageDeduplicationId=str(randint(10000, 99999)),
        MessageGroupId=str(randint(10000, 99999)),
        MessageAttributes=get_sqs_message_attributes(),
    )
    return True


def post_to_change_event_dlq(context: Context):
    queue_url = get_sqs_queue_name("changeevent")
    sqs_body = context.change_event.get_change_event()

    SQS_CLIENT.send_message(
        QueueUrl=queue_url,
        MessageBody=dumps(sqs_body),
        MessageDeduplicationId=str(randint(10000, 99999)),
        MessageGroupId=str(randint(10000, 99999)),
        MessageAttributes=get_sqs_message_attributes(context.change_event.odscode),
    )


def get_s3_email_file(context: Context) -> dict:
    sleep(45)
    shared_environment = getenv("SHARED_ENVIRONMENT")
    profile = getenv("PROFILE")
    bucket_name = f"uec-dos-int-{profile}-{shared_environment}-send-email-bucket"
    response = S3_CLIENT.list_objects(Bucket=bucket_name)
    object_key = response["Contents"][-1]["Key"]
    S3_RESOURCE = resource("s3")
    S3_RESOURCE.meta.client.download_file(bucket_name, object_key, "email_file.json")
    context.other = load(open("email_file.json", "r"))
    remove("email_file.json")
    return context
