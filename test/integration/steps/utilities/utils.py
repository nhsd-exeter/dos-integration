from ast import literal_eval
from datetime import datetime
from decimal import Decimal
from json import dumps, loads
from os import getenv
from random import sample, randrange
from time import sleep, time_ns, time
from typing import Any, Dict

from boto3 import client
from boto3.dynamodb.types import TypeDeserializer
from requests import Response, post, get

from .aws import get_secret
from .change_event import ChangeEvent
from .constants import SERVICE_TYPES

URL = getenv("URL")
CR_URL = getenv("CR_URL")
SQS_URL = getenv("SQS_URL")
EVENT_PROCESSOR = getenv("EVENT_PROCESSOR")
DYNAMO_DB_TABLE = getenv("DYNAMO_DB_TABLE")
LAMBDA_CLIENT_FUNCTIONS = client("lambda")
SQS_CLIENT = client("sqs", region_name="eu-west-2")
DYNAMO_CLIENT = client("dynamodb")
RDS_DB_CLIENT = client("rds")

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


def process_change_request_payload(change_event: ChangeEvent, valid_api_key: bool) -> Response:
    api_key = "invalid"
    if valid_api_key:
        secret = loads(get_secret(getenv("CR_API_KEY_SECRET")))
        api_key = secret[getenv("CR_API_KEY_KEY")]
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = change_event.get_change_event()
    output = post(url=CR_URL, headers=headers, data=dumps(payload))
    if valid_api_key and output.status_code != 200:
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
    response = invoke_test_db_checker_handler_lambda(lambda_payload)
    data = loads(response)
    data = literal_eval(data)
    return data


def get_pharmacy_odscode() -> str:
    lambda_payload = {"type": "get_single_service_pharmacy_odscode"}
    response = invoke_test_db_checker_handler_lambda(lambda_payload)
    data = loads(response)
    data = literal_eval(data)
    odscode = sample(tuple(data), 1)[0][0]
    return odscode


def get_single_service_pharmacy() -> str:
    ods_code = get_pharmacy_odscode()
    lambda_payload = {"type": "get_services_count", "odscode": ods_code}
    response = invoke_test_db_checker_handler_lambda(lambda_payload)
    data = loads(loads(response))[0][0]
    if data != 1:
        ods_code = get_single_service_pharmacy()
    return ods_code


def get_changes(correlation_id: str) -> list:
    lambda_payload = {"type": "get_changes", "correlation_id": correlation_id}
    response = invoke_test_db_checker_handler_lambda(lambda_payload)
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
    lambda_payload = {"type": "get_approver_status", "correlation_id": correlation_id}
    response = invoke_test_db_checker_handler_lambda(lambda_payload)
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


def get_service_id(correlation_id: str) -> list:
    retries = 0
    data = []
    data_status = False
    while data_status is False:
        lambda_payload = {"type": "get_service_id", "correlation_id": correlation_id}
        response = invoke_test_db_checker_handler_lambda(lambda_payload)
        data = loads(response)
        data = literal_eval(data)
        if data != []:
            return data[0][0]

        if retries > 16:
            raise ValueError("Error!.. Service Id not found")
        retries += 1
        sleep(30)


def get_service_type_from_cr(correlation_id: str) -> list:
    retries = 0
    data = []
    data_status = False
    while data_status is False:
        lambda_payload = {"type": "get_service_type_from_cr", "get_service_id": get_service_id(correlation_id)}
        response = invoke_test_db_checker_handler_lambda(lambda_payload)
        data = loads(response)
        data = literal_eval(data)
        if data != []:
            print(f"Number of service_type retries: {retries}")
            print(data)
            return data[0][0]

        if retries > 8:
            raise ValueError("Error!.. Service type not found")
        retries += 1
        sleep(5)


def get_service_type_data(organisation_type_id: str) -> list[int]:
    """Get the valid service types for the organisation type id"""
    return SERVICE_TYPES[organisation_type_id]


def get_change_event_demographics(odscode: str, organisation_type_id: str) -> Dict[str, Any]:
    lambda_payload = {
        "type": "change_event_demographics",
        "odscode": odscode,
        "organisation_type_id": organisation_type_id,
    }
    response = invoke_test_db_checker_handler_lambda(lambda_payload)
    data = loads(loads(response))
    return data


def get_change_event_standard_opening_times(service_id: str) -> Any:
    lambda_payload = {"type": "change_event_standard_opening_times", "service_id": service_id}
    response = invoke_test_db_checker_handler_lambda(lambda_payload)
    data = loads(response)
    data = literal_eval(data)
    return data


def get_change_event_specified_opening_times(service_id: str) -> Any:
    lambda_payload = {"type": "change_event_specified_opening_times", "service_id": service_id}
    response = invoke_test_db_checker_handler_lambda(lambda_payload)
    data = loads(response)
    data = literal_eval(data)
    return data


def get_odscode_with_contact_data() -> str:
    lambda_payload = {"type": "get_pharmacy_odscodes_with_contacts"}
    response = invoke_test_db_checker_handler_lambda(lambda_payload)
    data = loads(response)
    data = literal_eval(data)
    odscode = sample(data, 1)[0][0]
    return odscode


def invoke_test_db_checker_handler_lambda(lambda_payload: dict) -> Any:
    response_status = False
    response = None
    retries = 0
    while response_status is False:
        response: Any = LAMBDA_CLIENT_FUNCTIONS.invoke(
            FunctionName=getenv("TEST_DB_CHECKER_FUNCTION_NAME"),
            InvocationType="RequestResponse",
            Payload=dumps(lambda_payload),
        )
        response_payload = response["Payload"].read().decode("utf-8")
        if "errorMessage" not in response_payload:
            return response_payload

        if retries > 18:
            print(f"Error in this payload: {lambda_payload}")
            raise ValueError(f"Unable to run test db checker lambda successfully after {retries} retries")
        retries += 1
        sleep(10)


def check_received_data_in_dos(corr_id: str, search_key: str, search_param: str) -> bool:
    """NOT COMPATIBLE WITH OPENING TIMES CHANGES"""
    response = confirm_changes(corr_id)
    for row in response:
        change_value = dict(loads(row[0]))
        for dos_change_key in change_value["new"]:
            if dos_change_key == search_key and search_param in change_value["new"][dos_change_key]["data"]:
                return True
    return False


def check_specified_received_opening_times_date_in_dos(corr_id: str, search_key: str, search_param: str):
    """ONLY COMPATIBLE WITH OPENING TIMES CHANGES"""
    response = get_changes(corr_id)
    if_value_not_in_string_raise_exception(search_key, str(response))
    expected_date = datetime.strptime(search_param, "%b %d %Y").strftime("%d-%m-%Y")
    for db_row in response:
        change_row = dict(loads(db_row[0])["new"])
        if search_key in change_row and change_row[search_key]["changetype"] != "delete":
            for date in change_row[search_key]["data"]["add"]:
                if expected_date in date:
                    return True
    raise ValueError(f'Specified date change "{search_param}" not found in Dos changes..')


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


def check_specified_received_opening_times_time_in_dos(corr_id: str, search_key: str, search_param: str):
    """ONLY COMPATIBLE WITH OPENING TIMES CHANGES"""
    response = get_changes(corr_id)
    if_value_not_in_string_raise_exception(search_key, str(response))
    for db_row in response:
        change_row = dict(loads(db_row[0])["new"])
        if search_key in change_row and change_row[search_key]["changetype"] != "delete":
            time_periods = change_row[search_key]["data"]["add"]
            for time_period in time_periods:
                if search_param in time_period:
                    return True
    raise ValueError("Specified Opening-time time change not found in Dos changes..")


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
        lambda_payload = {"type": "get_pharmacy_odscodes"}
        PHARMACY_ODS_CODE_LIST = get_odscodes_list(lambda_payload)
    odscode_list = sample(PHARMACY_ODS_CODE_LIST, 1)[0]
    PHARMACY_ODS_CODE_LIST.remove(odscode_list)
    odscode = odscode_list[0]
    return odscode


def random_dentist_odscode() -> str:
    global DENTIST_ODS_CODE_LIST
    if DENTIST_ODS_CODE_LIST is None:
        lambda_payload = {"type": "get_dentist_odscodes"}
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


def slack_retry(message) -> str:
    counter = 0
    slack_channel = loads(get_secret("uec-dos-int-dev/deployment"))["SLACK_CHANNEL"]
    slack_oauth = loads(get_secret("uec-dos-int-dev/deployment"))["SLACK_OAUTH"]
    while counter < 10:
        sleep(10)
        responseVal = check_slack(slack_channel, slack_oauth)
        if message in responseVal:
            return responseVal
    raise ValueError("Slack alert message not found")


def check_slack(channel, token) -> str:
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
    }
    current = str(time() - 3600)

    output = get(url=f"https://slack.com/api/conversations.history?channel={channel}&oldest={current}", headers=headers)
    return output.text


def post_sqs_message():
    print("hit teh post sqs function")
    queue_url = "https://sqs.eu-west-2.amazonaws.com/730319765130/uec-dos-int-test-cr-dead-letter-queue.fifo"

    message = {
        "reference": "14451_1657015307500997089_//www.test.com]",
        "system": "DoS Integration",
        "message": "DoS Integration CR. correlation-id: 14451_1657015307500997089_//www.test.com]",
        "replace_opening_dates_mode": True,
        "service_id": "22963",
        "changes": {"website": "https://www.test.com"},
    }
    response = SQS_CLIENT.send_message(QueueUrl=queue_url, MessageBody=dumps(message))
    print(response)
    return True
