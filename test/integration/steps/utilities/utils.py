from ast import literal_eval
from datetime import datetime, timedelta
from decimal import Decimal
from json import dumps, loads
from os import getenv
from random import randint, randrange, sample
from re import sub
from time import sleep, time, time_ns
from typing import Any, Dict, Tuple

from boto3 import client
from boto3.dynamodb.types import TypeDeserializer
from pytz import UTC
from requests import get, post, Response

from .change_event import ChangeEvent
from .constants import SERVICE_TYPES
from .context import Context
from .secrets_manager import get_secret
from .translation import get_service_history_data_key

URL = getenv("URL")
CR_URL = getenv("CR_URL")
SQS_URL = getenv("SQS_URL")
EVENT_PROCESSOR = getenv("EVENT_PROCESSOR")
DYNAMO_DB_TABLE = getenv("DYNAMO_DB_TABLE")
CR_DLQ_NAME = getenv("CR_DLQ_NAME")
CE_DLQ_NAME = getenv("CE_DLQ_NAME")
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
    response = invoke_dos_db_handler_lambda(lambda_payload)
    data = loads(response)
    data = literal_eval(data)
    return data


def get_pharmacy_odscode() -> str:
    lambda_payload = {"type": "get_single_service_pharmacy_odscode"}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    data = loads(response)
    data = literal_eval(data)
    odscode = sample(tuple(data), 1)[0][0]
    return odscode


def get_single_service_pharmacy() -> str:
    # Runs this
    ods_code = get_pharmacy_odscode()
    lambda_payload = {"type": "get_services_count", "odscode": ods_code}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    data = loads(loads(response))[0][0]
    # Should this not be a while loop with a counter
    if data != 1:
        ods_code = get_single_service_pharmacy()
    return ods_code


def get_changes(correlation_id: str) -> list:
    lambda_payload = {"type": "get_changes", "correlation_id": correlation_id}
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
    lambda_payload = {"type": "get_approver_status", "correlation_id": correlation_id}
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


def get_service_id(correlation_id: str) -> list:
    retries = 0
    data = []
    data_status = False
    while data_status is False:
        lambda_payload = {"type": "get_service_id", "correlation_id": correlation_id}
        response = invoke_dos_db_handler_lambda(lambda_payload)
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
        response = invoke_dos_db_handler_lambda(lambda_payload)
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
    response = invoke_dos_db_handler_lambda(lambda_payload)
    data = loads(loads(response))
    return data


def get_change_event_standard_opening_times(service_id: str) -> Any:
    lambda_payload = {"type": "change_event_standard_opening_times", "service_id": service_id}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    data = loads(response)
    data = literal_eval(data)
    return data


def get_change_event_specified_opening_times(service_id: str) -> Any:
    lambda_payload = {"type": "change_event_specified_opening_times", "service_id": service_id}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    data = loads(response)
    data = literal_eval(data)
    return data


def get_odscode_with_contact_data() -> str:
    lambda_payload = {"type": "get_pharmacy_odscodes_with_contacts"}
    response = invoke_dos_db_handler_lambda(lambda_payload)
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
        # Call out to the lambda for request response with a valid service id
        response_payload = response["Payload"].read().decode("utf-8")
        if "errorMessage" not in response_payload:
            return response_payload

        if retries > 6:
            print(f"Error in this payload: {lambda_payload}")
            raise ValueError(f"Unable to run test db checker lambda successfully after {retries} retries")
        retries += 1
        sleep(10)


def get_service_table_field(service_id: str, field_name: str) -> Any:
    lambda_payload = {"type": "get_service_table_field", "service_id": service_id, "field": field_name}
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

    # Assert new data is correct

    assert (
        expected_data == changes[change_key]["data"]
    ), f"Expected data: {expected_data}, Expected data type: {type(expected_data)}, Actual data: {changes[change_key]['data']}"  # noqa

    # Assert previous data is correct
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


def get_service_history(service_id: str) -> Dict[str, Any]:
    lambda_payload = {"type": "get_service_history", "service_id": service_id}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    data = loads(loads(response))
    return loads(data[0][0])


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


def generate_untaken_ods() -> str:
    success = False
    while success is False:
        odscode = str(randint(10000, 99999))
        if check_ods_list(odscode) is True:
            return odscode


def check_ods_list(odscode: str) -> str:
    lambda_payload = {"type": "get_taken_odscodes"}
    ods_list = get_odscodes_list(lambda_payload)
    if odscode not in ods_list:
        return True
    else:
        return False


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
    slack_channel, slack_oauth = slack_secrets()
    for _ in range(6):
        sleep(60)
        response_value = check_slack(slack_channel, slack_oauth)
        if message in response_value:
            return response_value
    raise ValueError("Slack alert message not found")


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
    current_environment = getenv("ENVIRONMENT")
    match queue_type.lower():
        case "change event dlq":
            response = SQS_CLIENT.get_queue_url(
                QueueName=f"uec-dos-int-{current_environment}-change-event-dead-letter-queue.fifo",
            )
        case "cr":
            response = SQS_CLIENT.get_queue_url(
                QueueName=f"uec-dos-int-{current_environment}-update-request-dead-letter-queue.fifo",
            )
        case "404":
            response = SQS_CLIENT.get_queue_url(
                QueueName=f"uec-dos-int-{current_environment}-update-request-queue.fifo",
            )
        case _:
            raise ValueError("Invalid SQS queue type specified")
    print(response)
    raise NotImplementedError("Not implemented")

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


def post_cr_sqs():
    queue_url = get_sqs_queue_name("cr")
    sqs_body = generate_sqs_body("https://www.test.com")

    SQS_CLIENT.send_message(
        QueueUrl=queue_url,
        MessageBody=dumps(sqs_body),
        MessageDeduplicationId=str(randint(10000, 99999)),
        MessageGroupId=str(randint(10000, 99999)),
        MessageAttributes=get_sqs_message_attributes(),
    )
    return True


def post_cr_fifo():
    queue_url = get_sqs_queue_name("404")
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
    queue_url = get_sqs_queue_name("change event dlq")
    sqs_body = context.change_event.get_change_event()

    SQS_CLIENT.send_message(
        QueueUrl=queue_url,
        MessageBody=dumps(sqs_body),
        MessageDeduplicationId=str(randint(10000, 99999)),
        MessageGroupId=str(randint(10000, 99999)),
        MessageAttributes=get_sqs_message_attributes(context.change_event.odscode),
    )
