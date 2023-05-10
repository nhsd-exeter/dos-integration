from ast import literal_eval
from datetime import datetime, timedelta
from decimal import Decimal
from json import dumps, load, loads
from os import getenv, remove
from random import randint, randrange
from re import sub
from time import sleep, time, time_ns
from typing import Any

from boto3 import client, resource
from boto3.dynamodb.types import TypeDeserializer
from pytz import UTC, timezone
from requests import Response, get, post

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


def process_payload(context: Context, valid_api_key: bool | None, correlation_id: str) -> Response:
    """Process payload.

    Args:
        context (Context): Test context.
        valid_api_key (bool | None): Valid api key.
        correlation_id (str): Correlation id.

    Raises:
        ValueError: Unable to process change request payload.

    Returns:
        Response: Response from the API.
    """
    api_key = "invalid"
    if valid_api_key:
        api_key = loads(get_secret(getenv("API_KEY_SECRET")))[getenv("NHS_UK_API_KEY")]
    sequence_number = generate_unique_sequence_number(context.change_event["ODSCode"])
    headers = {
        "x-api-key": api_key,
        "sequence-number": sequence_number,
        "correlation-id": correlation_id,
        "Content-Type": "application/json",
    }
    payload = context.change_event
    output = post(url=URL, headers=headers, data=dumps(payload), timeout=10)
    if valid_api_key and output.status_code != 200:
        msg = f"Unable to process change request payload. Error: {output.text}"
        raise ValueError(msg)
    return output


def process_payload_with_sequence(context: Context, correlation_id: str, sequence_id: Any) -> Response:
    """Process payload with sequence.

    Args:
        context (Context): Test context.
        correlation_id (str): Correlation id.
        sequence_id (Any): Sequence id.
    """
    api_key = loads(get_secret(getenv("API_KEY_SECRET")))[getenv("NHS_UK_API_KEY")]
    headers = {
        "x-api-key": api_key,
        "correlation-id": correlation_id,
        "Content-Type": "application/json",
    }
    if sequence_id is not None:
        headers["sequence-number"] = str(sequence_id)
    payload = context.change_event
    output = post(url=URL, headers=headers, data=dumps(payload), timeout=10)
    if output.status_code != 200 and isinstance(sequence_id, int):
        msg = f"Unable to process change request payload. Error: {output.text}"
        raise ValueError(msg)
    return output


def get_stored_events_from_dynamo_db(odscode: str, sequence_number: Decimal) -> dict:
    """Get stored events from dynamodb.

    Args:
        odscode (str): ODSCode.
        sequence_number (Decimal): Sequence number.

    Raises:
        ValueError: No event found in dynamodb for ODSCode {odscode} and SequenceNumber {sequence_number}.

    Returns:
        dict: Stored events from dynamodb.
    """
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
        msg = f"No event found in dynamodb for ODSCode {odscode} and SequenceNumber {sequence_number}"
        raise ValueError(msg)
    item = resp["Items"][0]
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in item.items()}


def get_latest_sequence_id_for_a_given_odscode(odscode: str) -> int:
    """Get latest sequence id for a given odscode from dynamodb.

    Args:
        odscode (str): ODSCode.

    Raises:
        Exception: Unable to get sequence id from dynamodb

    Returns:
        int: Latest sequence id for a given odscode from dynamodb.
    """
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
    """Generate unique sequence number.

    Args:
        odscode (str): ODSCode.

    Returns:
        str: Unique sequence number.
    """
    return str(get_latest_sequence_id_for_a_given_odscode(odscode) + 1)


def generate_random_int(start_number: int = 1, stop_number: int = 1000) -> str:
    """Generate random int.

    Args:
        start_number (int, optional): Start number. Defaults to 1.
        stop_number (int, optional): Stop number. Defaults to 1000.

    Returns:
        str: Random int.
    """
    return str(randrange(start=start_number, stop=stop_number, step=1))


def get_single_service_pharmacy_odscode() -> dict:
    """Get single service pharmacy odscode.

    Returns:
        dict: Single service pharmacy odscode.
    """
    query = (
        "SELECT LEFT(odscode,5) FROM services WHERE typeid = 13 AND LENGTH(odscode) > 4 "
        "AND statusid = 1 AND odscode IS NOT NULL AND RIGHT(address, 1) != '$' "
        "AND publicphone IS NOT NULL AND web IS NOT NULL GROUP BY LEFT(odscode,5) HAVING COUNT(odscode) = 1"
    )
    lambda_payload = {"type": "read", "query": query, "query_vars": None}
    return invoke_dos_db_handler_lambda(lambda_payload)


def get_locations_table_data(postcode: str) -> list:
    """Get locations table data.

    Args:
        postcode (str): Postcode to search for in locations table.

    Returns:
        list: Locations table data.
    """
    query = (
        "SELECT postaltown as town, postcode, easting, northing, latitude, longitude "
        "FROM locations WHERE postcode = %(POSTCODE)s"
    )
    query_vars = {"POSTCODE": postcode}
    lambda_payload = {"type": "read", "query": query, "query_vars": query_vars}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    return loads(loads(response))


def get_services_table_location_data(service_id: str) -> list:
    """Get services table location data.

    Args:
        service_id (str): Service id to search for in services table.

    Returns:
        list: Services table location data.
    """
    query = "SELECT town, postcode, easting, northing, latitude, longitude FROM services WHERE id = %(SERVICE_ID)s"
    query_vars = {"SERVICE_ID": service_id}
    lambda_payload = {"type": "read", "query": query, "query_vars": query_vars}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    return loads(loads(response))


def get_service_id(odscode: str) -> str:
    """Get service id.

    Args:
        odscode (str): ODSCode.

    Returns:
        str: Service id.
    """
    data = []
    query = f"SELECT id FROM services WHERE typeid = 13 AND statusid = 1 AND odscode like '{odscode}%' LIMIT 1"  # noqa: S608,E501
    for _ in range(16):
        lambda_payload = {"type": "read", "query": query, "query_vars": None}
        response = invoke_dos_db_handler_lambda(lambda_payload)
        data = loads(response)
        data = literal_eval(data)
        if data != []:
            break
        sleep(30)
    else:
        msg = "Error!.. Service Id not found"
        raise ValueError(msg)
    return data[0]["id"]


def create_pending_change_for_service(service_id: str) -> None:
    """Create pending change for service.

    Args:
        service_id (str): Service id.
    """
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
        service_id,
        None,
        None,
        None,
    )
    lambda_payload = {"type": "write", "query": query, "query_vars": query_vars}
    invoke_dos_db_handler_lambda(lambda_payload)


def check_pending_service_is_rejected(service_id: str) -> Any:
    """Check pending service is rejected.

    Args:
        service_id (str): Service id.

    Returns:
        Any: Pending service is rejected.
    """
    query = "SELECT approvestatus FROM changes WHERE serviceid = %(SERVICE_ID)s"
    query_vars = {"SERVICE_ID": service_id}
    lambda_payload = {"type": "read", "query": query, "query_vars": query_vars}
    return invoke_dos_db_handler_lambda(lambda_payload)


def get_change_event_standard_opening_times(service_id: str) -> Any:
    """Get change event standard opening times.

    Args:
        service_id (str): Service id.

    Returns:
        Any: Change event standard opening times.
    """
    lambda_payload = {"type": "change_event_standard_opening_times", "service_id": service_id}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    return loads(response)


def get_change_event_specified_opening_times(service_id: str) -> Any:
    """Get change event specified opening times.

    Args:
        service_id (str): Service id.

    Returns:
        Any: Change event specified opening times.
    """
    lambda_payload = {"type": "change_event_specified_opening_times", "service_id": service_id}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    return loads(response)


def invoke_dos_db_handler_lambda(lambda_payload: dict) -> Any:
    """Invoke dos db handler lambda.

    Args:
        lambda_payload (dict): Lambda payload.

    Returns:
        Any: Lambda response.
    """
    response_status = False
    response = None
    retries = 0
    while not response_status:
        response: Any = LAMBDA_CLIENT_FUNCTIONS.invoke(
            FunctionName=getenv("DOS_DB_HANDLER"),
            InvocationType="RequestResponse",
            Payload=dumps(lambda_payload),
        )
        response_payload = response["Payload"].read().decode("utf-8")
        if "errorMessage" not in response_payload:
            return response_payload

        if retries > 6:
            msg = f"Unable to run test db checker lambda successfully after {retries} retries"
            raise ValueError(msg)
        retries += 1
        sleep(10)
    return None


def get_service_table_field(service_id: str, field_name: str) -> Any:
    """Get service table field.

    Args:
        service_id (str): Service id.
        field_name (str): Field name.

    Returns:
        Any: Service table field.
    """
    query = f"SELECT {field_name} FROM services WHERE id = %(SERVICE_ID)s"  # noqa: S608
    query_vars = {"SERVICE_ID": service_id}
    lambda_payload = {"type": "read", "query": query, "query_vars": query_vars}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    data = loads(loads(response))
    return data[0][field_name]


def wait_for_service_update(service_id: str) -> Any:
    """Wait for the service to be updated by checking modifiedtime."""
    for _ in range(12):
        sleep(10)
        updated_date_time_str: str = get_service_table_field(service_id, "modifiedtime")
        updated_date_time = datetime.strptime(updated_date_time_str, "%Y-%m-%d %H:%M:%S%z")
        updated_date_time = updated_date_time.replace(tzinfo=UTC)
        two_mins_ago = datetime.now(tz=timezone("Europe/London")) - timedelta(minutes=2)
        two_mins_ago = two_mins_ago.replace(tzinfo=UTC)
        if updated_date_time > two_mins_ago:
            break
    else:
        msg = f"Service not updated, service_id: {service_id}"
        raise ValueError(msg)


def get_expected_data(context: Context, changed_data_name: str) -> Any:
    """Get the previous data from the context."""
    match changed_data_name.lower():
        case "phone_no" | "phone" | "public_phone" | "publicphone":
            changed_data = context.phone
        case "website" | "web":
            changed_data = context.website
        case "address":
            changed_data = get_address_string(context)
        case "postcode":
            changed_data = context.change_event["Postcode"]
        case _:
            msg = f"Error!.. Input parameter '{changed_data_name}' not compatible"
            raise ValueError(msg)
    return changed_data


def get_address_string(context: Context) -> str:
    """Get the address string from the context.

    Args:
        context (Context): Test context

    Returns:
        str: Address string
    """
    address_lines = [
        line
        for line in [
            context.change_event["Address1"],
            context.change_event["Address2"],
            context.change_event["Address3"],
            context.change_event["City"],
            context.change_event["County"],
        ]
        if isinstance(line, str) and line.strip()
    ]
    address = "$".join(address_lines)
    address = sub(r"[A-Za-z]+('[A-Za-z]+)?", lambda word: word.group(0).capitalize(), address)
    address = address.replace("'", "")
    address = address.replace("&", "and")
    return address


def check_service_history(
    service_id: str,
    plain_english_field_name: str,
    expected_data: Any,
    previous_data: Any,
) -> None:
    """Check the service history for the expected data and previous data is removed."""
    service_history = get_service_history(service_id)
    first_key_in_service_history = list(service_history.keys())[0]
    changes = service_history[first_key_in_service_history]["new"]
    change_key = get_service_history_data_key(plain_english_field_name)
    if change_key not in changes:
        msg = f"DoS Change key '{change_key}' not found in latest service history entry"
        raise ValueError(msg)

    assert (
        expected_data == changes[change_key]["data"]
    ), f"Expected data: {expected_data}, Expected data type: {type(expected_data)}, Actual data: {changes[change_key]['data']}"  # noqa: E501

    # WTF is this? Why is this here? Why is this not a simple assert?
    if "previous" in changes[change_key] and previous_data != "unknown":
        if previous_data != "":  # noqa: PLC1901
            (
                changes[change_key]["previous"] == str(previous_data),
                f"Expected previous data: {previous_data}, Actual data: {changes[change_key]}",
            )
        elif previous_data == "":  # noqa: PLC1901
            assert (
                changes[change_key]["previous"] is None
            ), f"Expected previous data: {previous_data}, Actual data: {changes[change_key]}"
        else:
            msg = f"Input parameter '{previous_data}' not compatible"
            raise ValueError(msg)


def service_history_negative_check(service_id: str) -> str:
    """Check the service history for the expected data and previous data is removed.

    Args:
        service_id (str): Service ID of the service to be checked

    Returns:
        str: Returns a string based on the result of the check
    """
    service_history = get_service_history(service_id)
    if service_history == []:
        return "Not Updated"

    first_key_in_service_history = list(service_history.keys())[0]
    if check_recent_event(first_key_in_service_history) is False:
        return "Not Updated"
    return "Updated"


def check_service_history_change_type(service_id: str, change_type: str, field_name: None | str = None) -> str:
    """Check the service history for the expected change type.

    Args:
        service_id (str): Service ID of the service to be checked
        change_type (str): Change type to be checked
        field_name (str, optional): Field to search for in history. Defaults to None.

    Returns:
        str: Returns a string based on the result of the check
    """
    service_history = get_service_history(service_id)
    first_key_in_service_history = list(service_history.keys())[0]
    if field_name is None:
        change_status = service_history[first_key_in_service_history]["new"][
            list(service_history[first_key_in_service_history]["new"].keys())[0]
        ]["changetype"]
    else:
        change_status = service_history[first_key_in_service_history]["new"][field_name]["changetype"]
    if check_recent_event(first_key_in_service_history):
        if change_status == change_type or change_type == "modify" and change_status == "add":
            return "Change type matches"
        return "Change type does not match"
    return "No changes have been made"


def get_service_history_specified_opening_times(service_id: str) -> dict:
    """This function grabs the latest cmsopentimespecified object for a service id and returns it.

    Args:
        service_id (str): Service id to get service history for

    Returns:
        specified_open_times (dict): Specified opening times from service history
    """
    service_history = get_service_history(service_id)
    return service_history[list(service_history.keys())[0]]["new"]["cmsopentimespecified"]


def get_service_history_standard_opening_times(service_id: str) -> list:
    """This function grabs the latest standard opening times changes from service history.

    Args:
        service_id (str): Service id to get service history for

    Returns:
        standard_opening_times_from_service_history (list): List of standard opening times from service history
    """
    service_history = get_service_history(service_id)
    standard_opening_times_from_service_history = []
    for entry in service_history[list(service_history.keys())[0]]["new"]:
        if entry.endswith("day"):
            standard_opening_times_from_service_history.append(
                {entry: service_history[list(service_history.keys())[0]]["new"][entry]},
            )
    return standard_opening_times_from_service_history


def convert_specified_opening(specified_date: dict, closed_status: bool = False) -> str:
    """Converts opening times from CE format to DOS format.

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


def convert_standard_opening(standard_times: list[dict]) -> list[dict]:
    """Converts standard opening times from change event to be comparable with service history.

    Args:
        standard_times (list[dict]): Standard Opening times pulled from Change Event

    Returns:
        return_list (list[dict]): List of Dicts containing name of the day in cms format and times in seconds.
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


def assert_standard_openings(
    change_type: str,
    dos_times: list[dict],
    ce_times: list[dict],
    strict: bool | None = None,
) -> int:
    """Function to assert standard opening times changes. Added to remove complexity for sonar.

    Args:
        change_type (Str): The type of change being asserted
        dos_times (list[Dict]): The times pulled from DOS
        ce_times (Dict): The times pulled from the change event to compare too
        strict (bool | None): If true, will assert that the changetype is the same as the one passed in

    Returns:
        counter (Int): The amount of assertions made
    """
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


def assert_standard_closing(dos_times: list, ce_times: list[dict]) -> int:
    """Function to assert standard closing times changes.

    Args:
        dos_times (list): The times pulled from DOS
        ce_times (list): The times pulled from the change event to compare too

    Returns:
        int: If more than 0 assertions are made then the test passes.
    """
    counter = 0
    for entry in ce_times:
        if entry["times"] == "closed":
            currentday = entry["name"]
            for dates in dos_times:
                if currentday == list(dates.keys())[0]:
                    assert dates[currentday]["changetype"] == "delete", "Open when expected closed"
                    assert (
                        "add" not in dates[currentday]["data"]
                    ), "ERROR: Unexpected add field found in service history"
                    counter += 1
    return counter


def time_to_seconds(time: str) -> str:
    """Converts time to seconds.

    Args:
        time (str): The time to convert.

    Returns:
        str: The time in seconds.
    """
    times = time.split(":")
    hour_seconds = int(times[0]) * 3600
    minutes_seconds = int(times[1]) * 60
    return str(hour_seconds + minutes_seconds)


def check_recent_event(event_time: str, time_difference: int = 600) -> bool:
    """Checks if the event time is within the time difference.

    Args:
        event_time (str): The event time to check.
        time_difference (int, optional): Time difference in seconds. Defaults to 600.

    Returns:
        bool: True if the event time is within the time difference.
    """
    return int(time() - int(event_time)) <= time_difference


def get_service_history(service_id: str) -> list[dict[str, Any]]:
    """Gets the service history from the database.

    Args:
        service_id (str): The service id to get the history for.

    Returns:
        list[dict[str, Any]]: The service history.
    """
    data = []
    retry_counter = 0
    query = "SELECT history FROM servicehistories WHERE serviceid = %(SERVICE_ID)s"
    max_retry = 2
    while not data and retry_counter < max_retry:
        query_vars = {"SERVICE_ID": service_id}
        lambda_payload = {"type": "read", "query": query, "query_vars": query_vars}
        response = invoke_dos_db_handler_lambda(lambda_payload)
        data = loads(loads(response))
        retry_counter += 1
        sleep(30)
    return loads(data[0]["history"]) if data != [] else data


def generate_correlation_id(suffix: None | str = None) -> str:
    """Generates a correlation id for the lambda to use.

    Args:
        suffix (None | str): Suffix for correlation id. Defaults to None.

    Returns:
        str: Correlation id
    """
    name_no_space = getenv("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0].replace(" ", "_")
    run_id = getenv("RUN_ID")
    correlation_id = f"{run_id}_{time_ns()}_{name_no_space}" if suffix is None else f"{run_id}_{time_ns()}_{suffix}"
    correlation_id = (
        correlation_id if len(correlation_id) < 80 else correlation_id[:79]
    )  # DoS API Gateway max reference is 100 characters
    return correlation_id.replace("'", "")


def re_process_payload(odscode: str, seq_number: str) -> str:
    """Reprocesses a payload from the event replay lambda.

    Args:
        odscode (str): Odscode to send to lambda
        seq_number (str): Sequence number to send to lambda

    Returns:
        str: Response from lambda
    """
    lambda_payload = {"odscode": odscode, "sequence_number": seq_number}
    response = LAMBDA_CLIENT_FUNCTIONS.invoke(
        FunctionName=getenv("EVENT_REPLAY"),
        InvocationType="RequestResponse",
        Payload=dumps(lambda_payload),
    )
    return response["Payload"].read().decode("utf-8")


def slack_retry(message: str) -> str:
    """Retries slack message for 5 minutes.

    Args:
        message (str): Message to check for

    Raises:
        ValueError: If message is not found in slack

    Returns:
        str: Response from slack
    """
    slack_channel, slack_oauth = slack_secrets()
    for _ in range(6):
        sleep(60)
        response_value = check_slack(slack_channel, slack_oauth)
        if message in response_value:
            return response_value
    msg = f"Slack alert message not found, message: {message}"
    raise ValueError(msg)


def slack_secrets() -> tuple[str, str]:
    """Gets the slack secrets from AWS secrets manager.

    Returns:
        tuple[str, str]: Slack channel and slack oauth token
    """
    slack_secrets = loads(get_secret("uec-dos-int-dev/deployment"))
    return slack_secrets["SLACK_CHANNEL"], slack_secrets["SLACK_OAUTH"]


def check_slack(channel: str, token: str) -> str:
    """Gets slack messages for the specified channel.

    Args:
        channel (str): Slack channel to get messages for
        token (str): Slack token to use for authentication

    Returns:
        str: Response text from the slack API
    """
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
    }
    current = str(time() - 3600)
    output = get(
        url=f"https://slack.com/api/conversations.history?channel={channel}&oldest={current}",
        headers=headers,
        timeout=10,
    )
    return output.text


def get_sqs_queue_name(queue_type: str) -> str:
    """Returns the SQS queue name for the specified queue type.

    Args:
        queue_type (str): The type of SQS queue to return

    Returns:
        queue_name (str): The name of the SQS queue
    """
    response = ""
    blue_green_environment = getenv("BLUE_GREEN_ENVIRONMENT")
    shared_environment = getenv("SHARED_ENVIRONMENT")
    match queue_type.lower():
        case "changeevent":
            response = SQS_CLIENT.get_queue_url(
                QueueName=f"uec-dos-int-{shared_environment}-change-event-dead-letter-queue.fifo",
            )
        case "updaterequest":
            response = SQS_CLIENT.get_queue_url(
                QueueName=f"uec-dos-int-{blue_green_environment}-update-request-dead-letter-queue.fifo",
            )
        case "updaterequestfail":
            response = SQS_CLIENT.get_queue_url(
                QueueName=f"uec-dos-int-{blue_green_environment}-update-request-queue.fifo",
            )
        case _:
            msg = "Invalid SQS queue type specified"
            raise ValueError(msg)

    return response["QueueUrl"]


def get_sqs_message_attributes(odscode: str = "FW404") -> dict:
    """Generates a random set of message attributes for SQS.

    Args:
        odscode (str, optional): odscode to be added to message attributes. Defaults to "FW404".

    Returns:
        dict: message attributes
    """
    return {
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


def generate_sqs_body(website: str) -> dict:
    """Generate SQS body.

    Args:
        website (str): Website to update.

    Returns:
        dict: SQS body.
    """
    return {
        "reference": "14451_1657015307500997089_//www.test.com]",
        "system": "DoS Integration",
        "message": "DoS Integration CR. correlation-id: 14451_1657015307500997089_//www.test.com]",
        "replace_opening_dates_mode": True,
        "service_id": "22963",
        "changes": {"website": website},
    }


def post_ur_sqs() -> None:
    """Post to update request SQS queue."""
    queue_url = get_sqs_queue_name("updaterequest")
    sqs_body = generate_sqs_body("https://www.test.com")

    SQS_CLIENT.send_message(
        QueueUrl=queue_url,
        MessageBody=dumps(sqs_body),
        MessageDeduplicationId=str(randint(10000, 99999)),
        MessageGroupId=str(randint(10000, 99999)),
        MessageAttributes=get_sqs_message_attributes(),
    )


def post_ur_fifo() -> None:
    """Post to update request FIFO queue."""
    queue_url = get_sqs_queue_name("updaterequestfail")
    sqs_body = generate_sqs_body("abc@def.com")

    SQS_CLIENT.send_message(
        QueueUrl=queue_url,
        MessageBody=dumps(sqs_body),
        MessageDeduplicationId=str(randint(10000, 99999)),
        MessageGroupId=str(randint(10000, 99999)),
        MessageAttributes=get_sqs_message_attributes(),
    )


def post_to_change_event_dlq(context: Context) -> None:
    """Post to change event DLQ.

    Args:
        context (Context): Test context
    """
    queue_url = get_sqs_queue_name("changeevent")
    sqs_body = context.change_event

    SQS_CLIENT.send_message(
        QueueUrl=queue_url,
        MessageBody=dumps(sqs_body),
        MessageDeduplicationId=str(randint(10000, 99999)),
        MessageGroupId=str(randint(10000, 99999)),
        MessageAttributes=get_sqs_message_attributes(context.change_event["ODSCode"]),
    )


def get_s3_email_file(context: Context) -> Context:
    """Get the email file from S3 bucket.

    Args:
        context (Context): Test context

    Returns:
        context (Context): Test context
    """
    sleep(45)
    email_file_name = "email_file.json"
    shared_environment = getenv("SHARED_ENVIRONMENT")
    bucket_name = f"uec-dos-int-{shared_environment}-send-email-bucket"
    response = S3_CLIENT.list_objects(Bucket=bucket_name)
    object_key = response["Contents"][-1]["Key"]
    s3_resource = resource("s3")
    s3_resource.meta.client.download_file(bucket_name, object_key, email_file_name)
    with open(email_file_name) as email_file:
        context.other = load(email_file)
    remove("./email_file.json")
    return context
