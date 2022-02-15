from base64 import b64encode
from datetime import datetime
from decimal import Decimal
from json import dumps
from time import sleep, time
from os import getenv

from pytest_bdd import given, parsers, scenarios, then, when

from .utilities.events import build_same_as_dos_change_event, change_request, create_change_event
from .utilities.encryption import initialise_encryption_client
from .utilities.log_stream import get_logs
from .utilities.utils import (
    generate_correlation_id,
    get_changes,
    get_stored_events_from_dynamo_db,
    process_change_request_payload,
    process_payload,
    re_process_payload,
)

scenarios("../features/parent_features.feature", "../features/event_sender.feature", "../features/e2e_di_test.feature")


@given("a Changed Event is valid", target_fixture="context")
def a_change_event_is_valid():
    context = {}
    context["change_event"] = create_change_event()
    return context


@given("a Change Event which matches DoS", target_fixture="context")
def a_change_event_is_valid_and_matches_dos():
    context = {}
    context["change_event"] = build_same_as_dos_change_event()
    return context


@given("a valid unsigned change request", target_fixture="context")
def a_change_request_is_valid():
    context = {}
    context["change_request"] = change_request()
    return context


@given("a Changed Event with invalid ODSCode is provided", target_fixture="context")
def a_change_event_with_invalid_odscode():
    change_event = create_change_event()
    change_event["ODSCode"] = "F8KE1"
    context = {"change_event": change_event}
    return context


@given("change request has valid signature", target_fixture="context")
def has_valid_signature(context):
    key_data = {
        "ods_code": context["change_request"]["ods_code"],
        "dynamo_record_id": context["change_request"]["dynamo_record_id"],
        "message_received": context["change_request"]["message_received"],
        "time": time(),
    }
    encrypt_string = initialise_encryption_client()
    signing_key = encrypt_string(dumps(key_data))
    b64_mystring = b64encode(signing_key).decode("utf-8")
    context["change_request"]["signing_key"] = b64_mystring
    return context


@given("change request has invalid signature", target_fixture="context")
def has_invalid_signature(context):
    key_data = {
        "ods_code": "Dave",
        "dynamo_record_id": context["change_request"]["dynamo_record_id"],
        "message_received": context["change_request"]["message_received"],
        "time": time(),
    }
    encrypt_string = initialise_encryption_client()
    signing_key = encrypt_string(dumps(key_data))
    b64_mystring = b64encode(signing_key).decode("utf-8")
    context["change_request"]["signing_key"] = b64_mystring
    return context


@given("change request has expired signature", target_fixture="context")
def has_expired_signature(context):
    key_data = {
        "ods_code": "Dave",
        "dynamo_record_id": context["change_request"]["dynamo_record_id"],
        "message_received": context["change_request"]["message_received"],
        "time": time() - 100_000,
    }
    encrypt_string = initialise_encryption_client()
    signing_key = encrypt_string(dumps(key_data))
    b64_mystring = b64encode(signing_key).decode("utf-8")
    context["change_request"]["signing_key"] = b64_mystring
    return context


@given("a Changed Event contains an incorrect OrganisationSubtype", target_fixture="context")
def a_change_event_with_invalid_organisationsubtype():
    context = {}
    context["change_event"] = create_change_event()
    context["change_event"]["OrganisationSubType"] = "com"
    return context


@given("a Changed Event contains an incorrect OrganisationTypeID", target_fixture="context")
def a_change_event_with_invalid_organisationtypeid():
    context = {}
    context["change_event"] = create_change_event()
    context["change_event"]["OrganisationTypeId"] = "DEN"
    return context


# # Weekday NOT present on the Opening Time
@given("a Changed Event with the Weekday NOT present in the Opening Times data", target_fixture="context")
def a_change_event_with_no_openingtimes_weekday():
    context = {}
    context["change_event"] = create_change_event()
    del context["change_event"]["OpeningTimes"][0]["Weekday"]
    return context


# # OpeningTimeType is NOT "General" or "Additional"
@given("a Changed Event where OpeningTimeType is NOT defined correctly", target_fixture="context")
def a_change_event_with_invalid_openingtimetype():
    context = {}
    context["change_event"] = create_change_event()
    context["change_event"]["OpeningTimes"][0]["OpeningTimeType"] = "F8k3"
    return context


# set correlation id to contain "Bad Request"
@given(parsers.parse('the correlation-id is "{custom_correlation}"'), target_fixture="context")
def a_custom_correlation_id_is_set(context, custom_correlation: str):
    context["correlation_id"] = generate_correlation_id(custom_correlation)
    return context


# # isOpen is false AND Times in NOT blank
@given("a Changed Event with the openingTimes IsOpen status set to false", target_fixture="context")
def a_change_event_with_isopen_status_set_to_false():
    context = {}
    context["change_event"] = create_change_event()
    context["change_event"]["OpeningTimes"][0]["IsOpen"] = False
    return context


# # IsOpen is true AND Times is blank
@when("the OpeningTimes Opening and Closing Times data are not defined", target_fixture="context")
def no_times_data_within_openingtimes(context):
    context["change_event"] = changed_event()
    context["change_event"]["OpeningTimes"][0]["OpeningTime"] = ""
    context["change_event"]["OpeningTimes"][0]["ClosingTime"] = ""
    return context


# OpeningTimeType is Additional AND AdditionalOpening Date is Blank
@when(
    "the OpeningTimes OpeningTimeType is Additional and AdditionalOpeningDate is not defined",
    target_fixture="context",
)
def specified_opening_date_not_defined(context):
    context["change_event"] = create_change_event()
    context["change_event"]["OpeningTimes"][7]["AdditionalOpeningDate"] = ""
    return context


# # An OpeningTime is received for the Day or Date where IsOpen is True and IsOpen is false.
@when("an AdditionalOpeningDate contains data with both true and false IsOpen status", target_fixture="context")
def same_specified_opening_date_with_true_and_false_isopen_status(context):
    context["change_event"] = create_change_event()
    context["change_event"]["OpeningTimes"][7]["AdditionalOpeningDate"] = "Dec 25 2022"
    context["change_event"]["OpeningTimes"][7]["IsOpen"] = False
    return context


@when(
    parsers.parse('the Changed Event is sent for processing with "{valid_or_invalid}" api key'),
    target_fixture="context",
)
def the_change_event_is_sent_for_processing(context, valid_or_invalid):
    context["start_time"] = datetime.today().timestamp()
    if "correlation_id" not in context:
        context["correlation_id"] = generate_correlation_id()
    context["response"] = process_payload(
        context["change_event"], valid_or_invalid == "valid", context["correlation_id"]
    )
    context["sequence_no"] = context["response"].request.headers["sequence-number"]
    return context


@when("the postcode has no LAT Long values", target_fixture="context")
def postcode_with_no_lat_long_values(context):
    context["change_event"]["Postcode"] = "BT4 2HU"
    return context


@when(parsers.parse('the OrganisationStatus is defined as "{org_status}"'), target_fixture="context")
def a_change_event_with_orgstatus_value(context, org_status: str):
    context["change_event"]["OrganisationStatus"] = org_status
    return context


@when("the postcode is invalid", target_fixture="context")
def postcode_is_invalid(context):
    context["change_event"]["Postcode"] = "AAAA 123"
    return context


@when(parsers.parse('the change request is sent with "{valid_or_invalid}" api key'), target_fixture="context")
def the_change_request_is_sent(context, valid_or_invalid):
    context["start_time"] = datetime.today().timestamp()
    context["response"] = process_change_request_payload(context["change_request"], valid_or_invalid == "valid")
    return context


@then("no matched services were found")
def no_matched_services_found(context):
    query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context["correlation_id"]}"'
        ' | filter message like "Found 0 services in DB"'
    )
    event_logs = get_logs(query, "processor", context["start_time"])
    assert event_logs != [], "ERROR!! No unmatched services log found.."


@then("the Changed Event is stored in dynamo db")
def stored_dynamo_db_events_are_pulled(context):
    odscode = context["change_event"]["ODSCode"]
    sequence_num = Decimal(context["sequence_no"])
    sleep(10)
    db_event_record = get_stored_events_from_dynamo_db(odscode, sequence_num)
    assert db_event_record is not None, f"ERROR!! Event record with odscode {odscode} NOT found!.."
    assert (
        odscode == db_event_record["ODSCode"]
    ), f"ERROR!!.. Change event record({odscode} - {db_event_record['ODSCode']}) mismatch!!"
    assert sequence_num == db_event_record["SequenceNumber"], "ERROR!!.. Change event record(sequence no) mismatch!!"
    return context


@then("the unmatched service exception is reported to cloudwatch", target_fixture="context")
def unmatched_service_exception(context):
    query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context["correlation_id"]}"'
        ' | filter message like "No matching DOS services"'
    )
    logs = get_logs(query, "processor", context["start_time"])
    odscode = context["change_event"]["ODSCode"]
    assert f"ODSCode '{odscode}'" in logs, "ERROR!!.. Expected unmatched service logs not found."
    return context


@then("no Changed request is created", target_fixture="context")
def no_cr_created(context):
    query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context["correlation_id"]}"'
        ' | filter message = "No changes identified"'
    )
    logs = get_logs(query, "processor", context["start_time"])
    assert logs != [], "ERROR!!.. Unexpected Changed request found.."
    return context


@then("the exception is reported to cloudwatch", target_fixture="context")
def service_exception(context):
    query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context["correlation_id"]}"'
        ' | filter level="ERROR"'
    )
    logs = get_logs(query, "processor", context["start_time"])
    assert logs != [], "ERROR!!.. Expected exception not logged."
    return context


@then("the OpeningTimes exception is reported to cloudwatch")
def openingtimes_service_exception(context):
    query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context["correlation_id"]}"'
        ' | filter message like "Changes for nhs"'
    )
    logs = get_logs(query, "processor", context["start_time"])
    assert "opening_dates" not in logs, "ERROR!!.. Expected OpeningTimes exception not captured."


@then("the invalid postcode exception is reported to cloudwatch")
def unmatched_postcode_exception(context):
    query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context["correlation_id"]}"'
        ' | filter report_key like "INVALID_POSTCODE"'
    )
    logs = get_logs(query, "processor", context["start_time"])
    postcode = context["change_event"]["Postcode"]
    assert f"postcode '{postcode}'" in logs, "ERROR!!.. Expected Invalid Postcode exception not found."


@then("the hidden or closed exception is reported to cloudwatch")
def hidden_or_closed_exception(context):
    query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context["correlation_id"]}"'
        ' | filter message like "NHS Service marked as closed or hidden"'
    )
    logs = get_logs(query, "processor", context["start_time"])
    assert (
        "no change requests will be produced" in logs
    ), "ERROR!!.. Expected hidden or closed exception logs not found."


@then(parsers.parse("the {address} from the changes is not included in the change request"))
def address_change_is_discarded_in_event_sender(context, address: str):
    query = (
        f'fields change_request_body | sort @timestamp asc | filter correlation_id="{context["correlation_id"]}"'
        '| filter message like "Attempting to send change request to DoS"'
    )
    logs = get_logs(query, "sender", context["start_time"])
    assert f"{address}" not in logs, "ERROR!!.. Unexpected Address change found in logs."


@then("the processed Changed Request is sent to Dos", target_fixture="context")
def processed_changed_request_sent_to_dos(context):
    cr_received_search_param = "Received change request"
    cr_sent_search_param = "Successfully send change request to DoS"
    cr_received_query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context["correlation_id"]}"'
        f' | filter message like "{cr_received_search_param}"'
    )
    cr_sent_query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context["correlation_id"]}"'
        f' | filter message like "{cr_sent_search_param}"'
    )
    cr_received_logs = get_logs(cr_received_query, "sender", context["start_time"])
    assert cr_received_logs != [], "ERROR!!.. Expected Sender logs not found."
    cr_sent_logs = get_logs(cr_sent_query, "sender", context["start_time"])
    assert cr_sent_logs != [], "ERROR!!.. Expected sent event confirmation in service logs not found."
    return context


@then("the Changed Event is not processed any further")
def the_changed_event_is_not_processed(context):
    cr_received_search_param = "Received change request"
    query = f'fields message | sort @timestamp asc | filter correlation_id="{context["correlation_id"]}"'
    logs = get_logs(query, "processor", context["start_time"])
    assert f"{cr_received_search_param}" not in logs, "ERROR!!.. expected exception logs not found."


@then("the Changed Request is accepted by Dos")
def the_changed_request_is_accepted_by_dos(context):
    """assert dos API response and validate processed record in Dos CR Queue database"""
    response = get_changes(context["correlation_id"])
    assert response != [], "ERROR!!.. Expected Event confirmation in Dos not found."


@then("the Changed Event is not sent to Dos")
def the_changed_event_is_not_sent_to_dos(context):
    response = get_changes(context["correlation_id"])
    assert response == [], "ERROR!!.. Event data found in Dos."


@then("the event is sent to the DLQ", target_fixture="context")
def event_sender_triggers_DLQ(context):
    query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context["correlation_id"]}"'
        ' | filter response_text like "Fake Bad Request"'
    )
    logs = get_logs(query, "sender", context["start_time"])
    assert "Failed to send change request to DoS" in logs, "ERROR!!.. expected exception logs not found."
    return context


@then("the DLQ logs the error for Splunk", target_fixture="context")
def event_bridge_dlq_log_check(context):
    query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context["correlation_id"]}"'
        ' | filter report_key="EVENTBRIDGE_DLQ_HANDLER_RECEIVED_EVENT"'
    )
    logs = get_logs(query, "eb_dlq", context["start_time"])
    assert (
        "Eventbridge Dead Letter Queue Handler received event" in logs
    ), "ERROR!!.. expected exception logs not found."
    return context


@then(parsers.parse('the "{lambda_name}" logs show status code "{status_code}"'))
def lambda_status_code_check(context, lambda_name, status_code):
    query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context["correlation_id"]}"'
        f" | filter error_msg_http_code={status_code}"
    )
    logs = get_logs(query, lambda_name, context["start_time"])
    assert logs != [], "ERROR!!.. expected DLQ exception logs not found."


@then(parsers.parse('the "{lambda_name}" logs show error message "{error_message}"'))
def lambda_error_msg_check(context, lambda_name, error_message):
    query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context["correlation_id"]}"'
        f' | filter error_msg like "{error_message}"'
    )
    logs = get_logs(query, lambda_name, context["start_time"])
    assert logs != [], "ERROR!!.. expected DLQ exception logs not found."


@then(parsers.parse('the change request has status code "{status}"'))
def step_then_should_transform_into(context, status):
    message = context["response"].json
    assert (
        str(context["response"].status_code) == status
    ), f'Status code not as expected: {context["response"].status_code} != {status} Error: {message} - {status}'


@then("the attributes for invalid opening times report is identified in the logs")
def invalid_opening_times_exception(context):
    query = (
        f'fields @message | sort @timestamp asc | filter correlation_id="{context["correlation_id"]}"'
        '| filter report_key="INVALID_OPEN_TIMES"'
    )
    logs = get_logs(query, "processor", context["start_time"])
    for item in [
        "nhsuk_odscode",
        "nhsuk_organisation_name",
        "message_received",
        "nhsuk_open_times_payload",
        "dos_services",
    ]:
        assert item in logs


@then("the stored Changed Event is reprocessed in DI")
def replaying_changed_event(context):
    response = re_process_payload(context["change_event"]["ODSCode"], context["sequence_no"])
    assert "'StatusCode': 200" in str(response), f"Status code not as expected: {response}"


@then("the reprocessed Changed Event is sent to Dos")
def verify_replayed_changed_event(context):
    part_correlation_id = getenv("ENVIRONMENT") + "-replayed-event"
    odscode = context["change_event"]["ODSCode"]
    query = (
        f'fields message | sort @timestamp asc | filter correlation_id like "{part_correlation_id}"'
        f'| filter message like "Changes for nhs:{odscode}"'
    )
    logs = get_logs(query, "processor", context["start_time"])
    assert logs != [], "ERROR!!.. expected event-replay logs not found."
