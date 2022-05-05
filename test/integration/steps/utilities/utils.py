import random
from ast import literal_eval
from datetime import datetime
from decimal import Decimal
from json import dumps, loads
from os import getenv
from random import choice
from time import sleep, time_ns
from typing import Any, Dict

import requests
from boto3 import client
from boto3.dynamodb.types import TypeDeserializer
from requests import Response

from .aws import get_secret
from .constants import SERVICE_TYPES

URL = getenv("URL")
CR_URL = getenv("CR_URL")
SQS_URL = getenv("SQS_URL")
EVENT_PROCESSOR = getenv("EVENT_PROCESSOR")
DYNAMO_DB_TABLE = getenv("DYNAMO_DB_TABLE")
LAMBDA_CLIENT_FUNCTIONS = client("lambda")
SQS_CLIENT = client("sqs")
DYNAMO_CLIENT = client("dynamodb")
RDS_DB_CLIENT = client("rds")


def process_payload(payload: dict, valid_api_key: bool, correlation_id: str) -> Response:
    api_key = "invalid"
    if valid_api_key:
        api_key = loads(get_secret(getenv("API_KEY_SECRET")))[getenv("NHS_UK_API_KEY")]
    sequence_number = str(time_ns())
    headers = {
        "x-api-key": api_key,
        "sequence-number": sequence_number,
        "correlation-id": correlation_id,
        "Content-Type": "application/json",
    }
    payload["Unique_key"] = generate_random_int()
    output = requests.request("POST", URL, headers=headers, data=dumps(payload))
    return output


def process_payload_with_sequence(payload: dict, correlation_id: str, sequence_id) -> Response:
    api_key = loads(get_secret(getenv("API_KEY_SECRET")))[getenv("NHS_UK_API_KEY")]
    headers = {
        "x-api-key": api_key,
        "correlation-id": correlation_id,
        "Content-Type": "application/json",
    }
    if sequence_id is not None:
        headers["sequence-number"] = str(sequence_id)
    payload["Unique_key"] = generate_random_int()
    output = requests.request("POST", URL, headers=headers, data=dumps(payload))
    return output


def process_change_request_payload(payload: dict, api_key_valid: bool) -> Response:
    api_key = "invalid"
    if api_key_valid:
        secret = loads(get_secret(getenv("CR_API_KEY_SECRET")))
        api_key = secret[getenv("CR_API_KEY_KEY")]
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }
    output = requests.request("POST", CR_URL, headers=headers, data=dumps(payload))
    return output


def get_stored_events_from_dynamo_db(odscode: str, sequence_number: Decimal) -> dict:
    print(f"{DYNAMO_DB_TABLE} {odscode} {sequence_number}")
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
        KeyConditionExpression="ODSCode = :v1 and SequenceNumber = :v2 ",
        Limit=1,
        ScanIndexForward=False,
    )
    item = resp["Items"][0]
    deserializer = TypeDeserializer()
    deserialized = {k: deserializer.deserialize(v) for k, v in item.items()}
    return deserialized


def get_lambda_info(info_param: str) -> str:
    values = {"state": "State", "status": "LastUpdateStatus", "description": "Description"}
    param = values[info_param]
    response = LAMBDA_CLIENT_FUNCTIONS.get_function(FunctionName=EVENT_PROCESSOR)
    return response["Configuration"][param]


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


def generate_random_int() -> str:
    return str(random.sample(range(1000), 1)[0])


def get_odscodes_list(lambda_payload: dict) -> list[list[str]]:
    response = invoke_test_db_checker_handler_lambda(lambda_payload)
    data = loads(response)
    data = literal_eval(data)
    return data


def get_single_service_odscode() -> str:
    lambda_payload = {"type": "get_single_pharmacy_service_odscode"}
    response = invoke_test_db_checker_handler_lambda(lambda_payload)
    data = loads(response)
    data = literal_eval(data)
    odscode = choice(data)[0]
    return odscode


def get_changes(correlation_id: str) -> list:
    lambda_payload = {"type": "get_changes", "correlation_id": correlation_id}
    response = invoke_test_db_checker_handler_lambda(lambda_payload)
    data = loads(loads(response))
    return data


def confirm_changes(correlation_id: str) -> list:
    changes_loop_count = 0
    data = []
    while changes_loop_count < 12:
        sleep(10)
        data = get_changes(correlation_id)
        if data != []:
            break
        changes_loop_count += 1
    print(f"Number of confirm-changes retries: {changes_loop_count}")
    return data


def get_approver_status(correlation_id: str) -> list:
    lambda_payload = {"type": "get_approver_status", "correlation_id": correlation_id}
    response = invoke_test_db_checker_handler_lambda(lambda_payload)
    data = loads(loads(response))
    return data


def confirm_approver_status(correlation_id: str) -> list:
    approver_loop_count = 0
    data = []
    while approver_loop_count < 15:
        sleep(60)
        data = get_approver_status(correlation_id)
        if data != []:
            break
        approver_loop_count += 1
    print(f"Number of approver retries: {approver_loop_count}")
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
            print(f"Number of service_id retries: {retries}")
            print(data)
            return data[0][0]

        if retries > 8:
            raise Exception("Error!.. Service Id not found")
        retries += 1
        sleep(5)


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
            raise Exception("Error!.. Service type not found")
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
    odscode = choice(data)[0]
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

        if retries > 9:
            print(f"Errored on this payload: {lambda_payload}")
            raise Exception(f"Unable to run test db checker lambda successfully after {retries} retries")
        retries += 1
        sleep(20)


def check_received_data_in_dos(corr_id: str, search_key: str, search_param: str):
    """NOT COMPATIBLE WITH OPENING TIMES CHANGES"""
    response = confirm_changes(corr_id)
    if search_key not in str(response):
        raise ValueError(f"{search_key} not found..")
    for row in response:
        change_value = dict(loads(row[0]))
        for dos_change_key in change_value["new"]:
            if dos_change_key == search_key and search_param in change_value["new"][dos_change_key]["data"]:
                return True
    raise ValueError(f"{search_param} not found in Dos changes... {response}")


def check_specified_received_opening_times_date_in_dos(corr_id: str, search_key: str, search_param: str):
    """ONLY COMPATIBLE WITH OPENING TIMES CHANGES"""
    response = get_changes(corr_id)
    if search_key not in str(response):
        raise ValueError(f"{search_key} not found..")
    row_found = False
    for row in response:
        for k in dict(loads(row[0]))["new"]:
            if k == search_key:
                if dict(loads(row[0]))["new"][k]["changetype"] != "delete":
                    date_in_dos = dict(loads(row[0]))["new"][k]["data"]["add"][0][:10]
                    # Convert and format 'search_param' to datetime type
                    date_in_payload = datetime.strptime(search_param, "%b %d %Y").strftime("%d-%m-%Y")
                    if date_in_dos == date_in_payload:
                        row_found = True
    if row_found is True:
        return True
    else:
        raise ValueError(f'Specified date change "{date_in_payload}" not found in Dos changes..')


def check_contact_delete_in_dos(corr_id: str, search_key: str):
    response = get_changes(corr_id)
    if search_key not in str(response):
        raise ValueError(f"{search_key} not found..")
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
    if search_key not in str(response):
        raise ValueError(f"{search_key} not found..")
    row_found = False
    for row in response:
        for k in dict(loads(row[0]))["new"]:
            if k == search_key:
                if dict(loads(row[0]))["new"][k]["changetype"] != "delete":
                    time_in_dos = dict(loads(row[0]))["new"][k]["data"]["add"][0][11:]
                    if time_in_dos == search_param:
                        row_found = True
    if row_found is True:
        return True
    else:
        raise ValueError("Specified Opening-time time change not found in Dos changes..")


def check_standard_received_opening_times_time_in_dos(corr_id: str, search_key: str, search_param: str):
    """ONLY COMPATIBLE WITH OPENING TIMES CHANGES"""
    response = get_changes(corr_id)
    if search_key not in str(response):
        raise ValueError(f"{search_key} not found..")
    for row in response:
        for k in dict(loads(row[0]))["new"]:
            if k == search_key:
                time_in_dos = dict(loads(row[0]))["new"][k]["data"]["add"][0]
                if time_in_dos == search_param:
                    return True
                else:
                    raise ValueError("Standard Opening-time time change not found in Dos changes... {response}")


def time_to_sec(t):
    h, m = map(int, t.split(":"))
    return (h * 3600) + (m * 60)


def generate_correlation_id(prefix=None) -> str:
    name_no_space = getenv("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0].replace(" ", "_")
    run_id = getenv("RUN_ID")
    correlation_id = f"{run_id}_{name_no_space}" if prefix is None else f"{prefix}_{run_id}"
    correlation_id = (
        correlation_id if len(correlation_id) < 80 else correlation_id[:79]
    )  # DoS API Gateway max reference is 100 characters
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
