import secrets
import string
from json import dumps, loads
from os import getenv
from random import randint, randrange
from re import sub
from time import time, time_ns
from typing import Any

from .aws.aws_lambda import invoke_dos_db_handler_lambda
from .aws.cloudwatch import get_logs, negative_log_check
from .aws.dynamodb import get_latest_sequence_id_for_a_given_odscode
from .context import Context


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


def get_expected_data(context: Context, changed_data_name: str) -> Any:
    """Get the previous data from the context."""
    match changed_data_name.lower():
        case "phone_no" | "phone" | "public_phone" | "publicphone":
            changed_data = context.generator_data["publicphone"]
        case "website" | "web":
            changed_data = context.generator_data["web"]
        case "address" | "address1":
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
    return address.replace("&", "and")


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
    if closed_status:
        return f"{split_date[2]}-{selected_month}-{split_date[1]}-closed"
    opening_time = time_to_seconds(specified_date["OpeningTime"])
    closing_time = time_to_seconds(specified_date["ClosingTime"])
    return f"{split_date[2]}-{selected_month}-{split_date[1]}-{opening_time}-{closing_time}"


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


def quality_checker_log_check(
    request_id: str,
    odscode: str,
    reason: str,
    start_time: str,
    match_on_more_than_5_character_odscode: bool = False,
) -> list[dict]:
    """Check logs for quality checker.

    Args:
        request_id (str): Quality checker function request id
        odscode (str): ODS code
        reason (str): Reason for quality check
        start_time (str): Start time for the query
        match_on_more_than_5_character_odscode (bool): Match on more than 5 character odscode.  Defaults to False.

    Returns:
        list[dict]: logs
    """
    query = f"""fields message
| filter function_request_id="{request_id}"
| filter report_key="QUALITY_CHECK_REPORT_KEY"
| filter {'dos_service_odscode' if match_on_more_than_5_character_odscode else 'odscode'}="{odscode}"
| filter message="{reason}"
| sort @timestamp asc"""
    results = loads(get_logs(query=query, lambda_name="quality-checker", start_time=start_time))
    return results["results"]


def quality_checker_negative_log_check(
    request_id: str,
    odscode: str,
    reason: str,
    start_time: str,
    match_on_more_than_5_character_odscode: bool = False,
) -> bool:
    """Check no logs for quality checker.

    Args:
        request_id (str): Quality checker function request id
        odscode (str): ODS code
        reason (str): Reason for quality check
        start_time (str): Start time for the query
        match_on_more_than_5_character_odscode (bool): Match on more than 5 character odscode.  Defaults to False.

    Returns:
        bool: True if no logs found
    """
    query = f"""fields message
| filter function_request_id="{request_id}"
| filter report_key="QUALITY_CHECK_REPORT_KEY"
| filter {'dos_service_odscode' if match_on_more_than_5_character_odscode else 'odscode'}="{odscode}"
| filter message="{reason}"
| sort @timestamp asc"""
    return negative_log_check(query=query, event_lambda="quality-checker", start_time=start_time)


def generate_unique_ods_code() -> str:
    """Generate a unique 5-character uppercase alphanumeric ODSCode."""
    chars = string.ascii_uppercase + string.digits  # A-Z, 0-9
    return "".join(secrets.choice(chars) for _ in range(5))  # 5-character random string
