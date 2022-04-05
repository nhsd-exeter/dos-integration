from datetime import datetime as dt
from decimal import Decimal
from time import sleep, time
from os import getenv
from random import randint
from faker import Faker
import datetime
from json import loads
import ast

from pytest_bdd import given, parsers, scenarios, then, when

from .utilities.events import (
    build_same_as_dos_change_event,
    change_request,
    create_pharmacy_change_event,
    set_opening_times_change_event,
    valid_change_event,
)

from .utilities.aws import get_logs
from .utilities.utils import (
    generate_correlation_id,
    get_changes,
    get_service_id,
    get_change_event_standard_opening_times,
    get_change_event_specified_opening_times,
    confirm_approver_status,
    get_stored_events_from_dynamo_db,
    process_change_request_payload,
    process_payload,
    process_payload_with_sequence,
    re_process_payload,
    get_latest_sequence_id_for_a_given_odscode,
    check_received_data_in_dos,
    check_standard_received_opening_times_time_in_dos,
    check_specified_received_opening_times_time_in_dos,
    check_specified_received_opening_times_date_in_dos,
    time_to_sec,
    confirm_changes,
    get_service_type_data,
    get_service_type_from_cr,
)

scenarios(
    "../features/F001_Valid_Change_Events.feature",
    "../features/F002_Invalid_Change_Events.feature",
    "../features/F003_DoS_Security.feature",
    "../features/F004_Error_Handling.feature",
    "../features/F005_Support_Functions.feature",
    "../features/F006_Opening_times.feature",
)
FAKER = Faker("en_GB")


@given("a Changed Event is valid", target_fixture="context")
def a_change_event_is_valid():
    context = {}
    context["change_event"] = create_pharmacy_change_event()
    return context


@given("a Dentist Changed Event is valid", target_fixture="context")
def valid_dentist_change_event():
    context = {}
    context["change_event"] = create_pharmacy_change_event()
    context["change_event"]["ODSCode"] = "V01521"
    context["change_event"]["OrganisationName"] = "Test Dentist"
    context["change_event"]["OrganisationTypeId"] = "Dentist"
    context["change_event"]["OrganisationSubType"] = "TBA"
    context["change_event"]["Address1"] = FAKER.street_name()
    return context


@given(parsers.parse('a Changed Event with changed "{contact}" is valid'), target_fixture="context")
def a_changed_contact_event_is_valid(contact):
    context = {}
    context["change_event"] = create_pharmacy_change_event()
    validated = False
    while validated is False:
        if contact == "website":
            context["change_event"]["Contacts"][0]["ContactValue"] = FAKER.domain_word() + ".nhs.uk"
        elif contact == "phone_no":
            context["change_event"]["Contacts"][1]["ContactValue"] = FAKER.phone_number()
        elif contact == "address":
            context["change_event"]["Address1"] = FAKER.street_name()
        else:
            raise ValueError(f"ERROR!.. Input parameter '{contact}' not compatible")

        validated = valid_change_event(context["change_event"])
    return context


@given("a specific Changed Event is valid", target_fixture="context")
def a_specific_change_event_is_valid():
    context = {}
    context["change_event"] = set_opening_times_change_event()
    return context


@given("an opened specified opening time Changed Event is valid", target_fixture="context")
def a_specified_opening_time_change_event_is_valid():
    closing_time = datetime.datetime.now().time().strftime("%H:%M")
    context = {}
    context["change_event"] = set_opening_times_change_event()
    context["change_event"]["OpeningTimes"][-1]["OpeningTime"] = "00:01"
    context["change_event"]["OpeningTimes"][-1]["ClosingTime"] = closing_time
    context["change_event"]["OpeningTimes"][-1]["IsOpen"] = True
    return context


@given("an opened standard opening time Changed Event is valid", target_fixture="context")
def a_standard_opening_time_change_event_is_valid():
    closing_time = datetime.datetime.now().time().strftime("%H:%M")
    context = {}
    context["change_event"] = set_opening_times_change_event()
    context["change_event"]["OpeningTimes"][-2]["Weekday"] = "Monday"
    context["change_event"]["OpeningTimes"][-2]["OpeningTime"] = "00:01"
    context["change_event"]["OpeningTimes"][-2]["ClosingTime"] = closing_time
    context["change_event"]["OpeningTimes"][-2]["IsOpen"] = True
    return context


@given("a Changed Event is aligned with Dos", target_fixture="context")
def a_change_event_is_valid_and_matches_dos():
    context = {}
    context["change_event"] = build_same_as_dos_change_event()
    return context


@given("a valid unsigned change request", target_fixture="context")
def a_change_request_is_valid():
    context = {}
    context["change_request"] = change_request()
    return context


@given("the Changed Event has overlapping opening times", target_fixture="context")
def change_event_with_overlapping_opening_times(context):
    context["change_event"]["OpeningTimes"][0]["ClosingTime"] = "12:00"
    context["change_event"]["OpeningTimes"][1]["Weekday"] = "Monday"
    context["change_event"]["OpeningTimes"][1]["OpeningTime"] = "11:00"
    return context


@given("the Changed Event has one break in opening times", target_fixture="context")
def change_event_with_break_in_opening_times(context):
    context["change_event"]["OpeningTimes"][0]["ClosingTime"] = "11:00"
    context["change_event"]["OpeningTimes"][1]["Weekday"] = "Monday"
    context["change_event"]["OpeningTimes"][1]["OpeningTime"] = "12:00"
    return context


@given("the Changed Event has two breaks in opening times", target_fixture="context")
def change_event_with_two_breaks_in_opening_times(context):
    context["change_event"]["OpeningTimes"][0]["ClosingTime"] = "11:00"
    context["change_event"]["OpeningTimes"][1]["Weekday"] = "Monday"
    context["change_event"]["OpeningTimes"][1]["OpeningTime"] = "12:00"
    context["change_event"]["OpeningTimes"][1]["ClosingTime"] = "14:00"
    context["change_event"]["OpeningTimes"][2]["Weekday"] = "Monday"
    context["change_event"]["OpeningTimes"][2]["OpeningTime"] = "16:00"
    return context


@given("the website field contains special characters", target_fixture="context")
def change_event_with_special_address_characters(context):
    uniqueval = int(time())
    context["change_event"]["Contacts"][0][
        "ContactValue"
    ] = f"https:\/\/www.rowlandspharmacy.co.uk\/test?foo={uniqueval}"  # noqa: W605
    context["uri_timestamp"] = uniqueval
    return context


@given(
    parsers.parse('the Changed Event contains a one off opening date thats "{open_closed}"'), target_fixture="context"
)
def one_off_opening_date_set(context, open_closed: str):
    context["change_event"]["OpeningTimes"][0]["OpeningTimeType"] = "Additional"
    selectedday = randint(10, 30)
    context["change_event"]["OpeningTimes"][0]["AdditionalOpeningDate"] = f"Dec {selectedday} 2025"
    context["change_event"]["OpeningTimes"][0]["Weekday"] = ""
    if open_closed.lower() == "open":
        context["change_event"]["OpeningTimes"][0]["OpeningTime"] = "09:00"
        context["change_event"]["OpeningTimes"][0]["ClosingTime"] = "17:00"
        context["change_event"]["OpeningTimes"][0]["IsOpen"] = True
    elif open_closed.lower() == "closed":
        context["change_event"]["OpeningTimes"][0]["OpeningTime"] = ""
        context["change_event"]["OpeningTimes"][0]["ClosingTime"] = ""
        context["change_event"]["OpeningTimes"][0]["IsOpen"] = False
    return context


@given("the Changed Event closes the pharmacy on a bank holiday", target_fixture="context")
def bank_holiday_pharmacy_closed(context):
    context["change_event"]["OpeningTimes"][0]["OpeningTimeType"] = "Additional"
    nextyear = dt.now().year + 1
    context["change_event"]["OpeningTimes"][0]["AdditionalOpeningDate"] = f"Dec 25 {nextyear}"
    context["change_event"]["OpeningTimes"][0]["Weekday"] = ""
    context["change_event"]["OpeningTimes"][0]["OpeningTime"] = ""
    context["change_event"]["OpeningTimes"][0]["ClosingTime"] = ""
    context["change_event"]["OpeningTimes"][0]["IsOpen"] = False
    return context


@given("a Changed Event with invalid ODSCode is provided", target_fixture="context")
def a_change_event_with_invalid_odscode():
    change_event = create_pharmacy_change_event()
    change_event["ODSCode"] = "F8KE1"
    context = {"change_event": change_event}
    return context


@given(parsers.parse('the Changed Event has ODS Code "{odscode}"'), target_fixture="context")
def a_change_event_with_custom_ods(context, odscode: str):
    context["change_event"]["ODSCode"] = odscode
    return context


@given("a Changed Event contains an incorrect OrganisationSubtype", target_fixture="context")
def a_change_event_with_invalid_organisationsubtype():
    context = {}
    context["change_event"] = create_pharmacy_change_event()
    context["change_event"]["OrganisationSubType"] = "com"
    return context


@given("a Changed Event contains an incorrect OrganisationTypeID", target_fixture="context")
def a_change_event_with_invalid_organisationtypeid():
    context = {}
    context["change_event"] = create_pharmacy_change_event()
    context["change_event"]["OrganisationTypeId"] = "DEN"
    return context


# # Weekday NOT present on the Opening Time
@given("a Changed Event with the Weekday NOT present in the Opening Times data", target_fixture="context")
def a_change_event_with_no_openingtimes_weekday():
    context = {}
    context["change_event"] = create_pharmacy_change_event()
    del context["change_event"]["OpeningTimes"][0]["Weekday"]
    return context


# # OpeningTimeType is NOT "General" or "Additional"
@given("a Changed Event where OpeningTimeType is NOT defined correctly", target_fixture="context")
def a_change_event_with_invalid_openingtimetype():
    context = {}
    context["change_event"] = create_pharmacy_change_event()
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
    context["change_event"] = create_pharmacy_change_event()
    context["change_event"]["OpeningTimes"][0]["IsOpen"] = False
    return context


# # Check that the requested ODS code exists in ddb, and create an entry if not
@given("an ODS has an entry in dynamodb", target_fixture="context")
def current_ods_exists_in_ddb():
    context = {}
    context["change_event"] = create_pharmacy_change_event()
    odscode = context["change_event"]["ODSCode"]
    if get_latest_sequence_id_for_a_given_odscode(odscode) == 0:
        context = the_change_event_is_sent_with_custom_sequence(context, 100)
    # New address prevents SQS dedupe
    newaddr = randint(100, 500)
    context["change_event"]["Address1"] = f"{newaddr} New Street"
    return context


# # IsOpen is true AND Times is blank
@when("the OpeningTimes Opening and Closing Times data are not defined", target_fixture="context")
def no_times_data_within_openingtimes(context):
    context["change_event"] = create_pharmacy_change_event()
    context["change_event"]["OpeningTimes"][0]["OpeningTime"] = ""
    context["change_event"]["OpeningTimes"][0]["ClosingTime"] = ""
    return context


# OpeningTimeType is Additional AND AdditionalOpening Date is Blank
@when(
    "the OpeningTimes OpeningTimeType is Additional and AdditionalOpeningDate is not defined",
    target_fixture="context",
)
def specified_opening_date_not_defined(context):
    context["change_event"] = create_pharmacy_change_event()
    context["change_event"]["OpeningTimes"][7]["AdditionalOpeningDate"] = ""
    return context


# # An OpeningTime is received for the Day or Date where IsOpen is True and IsOpen is false.
@when("an AdditionalOpeningDate contains data with both true and false IsOpen status", target_fixture="context")
def same_specified_opening_date_with_true_and_false_isopen_status(context):
    context["change_event"] = create_pharmacy_change_event()
    context["change_event"]["OpeningTimes"][7]["AdditionalOpeningDate"] = "Dec 25 2022"
    context["change_event"]["OpeningTimes"][7]["IsOpen"] = False
    return context


@when(
    parsers.parse('the Changed Event is sent for processing with "{valid_or_invalid}" api key'),
    target_fixture="context",
)
def the_change_event_is_sent_for_processing(context, valid_or_invalid):
    context["start_time"] = dt.today().timestamp()
    if "correlation_id" not in context:
        context["correlation_id"] = generate_correlation_id()
    context["response"] = process_payload(
        context["change_event"], valid_or_invalid == "valid", context["correlation_id"]
    )
    context["sequence_no"] = context["response"].request.headers["sequence-number"]
    print(f"Applied Correlation id: {context['correlation_id']}")
    return context


# # Request with custom sequence id
@when(
    parsers.parse("the Changed Event is sent for processing with sequence id {seqid}"),
    target_fixture="context",
)
def the_change_event_is_sent_with_custom_sequence(context, seqid):
    context["start_time"] = dt.today().timestamp()
    context["correlation_id"] = generate_correlation_id()
    context["response"] = process_payload_with_sequence(context["change_event"], context["correlation_id"], seqid)
    context["sequence_no"] = seqid
    return context


# # Request with no sequence id
@when(
    parsers.parse("the Changed Event is sent for processing with no sequence id"),
    target_fixture="context",
)
def the_change_event_is_sent_with_no_sequence(context):
    context["start_time"] = dt.today().timestamp()
    context["correlation_id"] = generate_correlation_id()
    context["response"] = process_payload_with_sequence(context["change_event"], context["correlation_id"], None)
    return context


# # Request with duplicate sequence id
@when(
    parsers.parse("the Changed Event is sent for processing with a duplicate sequence id"),
    target_fixture="context",
)
def the_change_event_is_sent_with_duplicate_sequence(context):
    context["start_time"] = dt.today().timestamp()
    context["correlation_id"] = generate_correlation_id()
    odscode = context["change_event"]["ODSCode"]
    seqid = get_latest_sequence_id_for_a_given_odscode(odscode)
    context["response"] = process_payload_with_sequence(context["change_event"], context["correlation_id"], seqid)
    context["sequence_no"] = seqid
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


@then("the unmatched service type exception is reported to cloudwatch")
def unmatched_service_type_exception(context):
    query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context["correlation_id"]}"'
        ' | filter report_key like "UNMATCHED_SERVICE_TYPE"'
    )
    logs = get_logs(query, "processor", context["start_time"])
    odscode = context["change_event"]["ODSCode"]
    assert f"{odscode}" in logs, "ERROR!!.. Expected Unmatched Service Type exception not found."


@then("the generic bank holiday exception is reported to cloudwatch")
def generic_bank_holiday_exception(context):
    query = (
        f'fields message, ods_code | sort @timestamp asc | filter correlation_id="{context["correlation_id"]}"'
        ' | filter report_key like "GENERIC_BANK_HOLIDAY"'
    )
    logs = get_logs(query, "processor", context["start_time"])
    odscode = context["change_event"]["ODSCode"]
    assert f"{odscode}" in logs, "ERROR!!.. Expected Generic Bank Holiday exception not found."


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
    response = confirm_changes(context["correlation_id"])
    assert response != [], "ERROR!!.. Expected Event confirmation in Dos not found."
    return context


@then(parsers.parse('the Changed Request with changed "{contact}" is captured by Dos'))
def the_changed_contact_is_accepted_by_dos(context, contact):
    """assert dos API response and validate processed record in Dos CR Queue database"""
    if contact == "phone_no":
        cms = "cmstelephoneno"
        changed_data = context["change_event"]["Contacts"][1]["ContactValue"]
    elif contact == "website":
        cms = "cmsurl"
        changed_data = context["change_event"]["Contacts"][0]["ContactValue"]
    else:
        raise ValueError(f"Error!.. Input parameter '{contact}' not compatible")
    assert (
        check_received_data_in_dos(context["correlation_id"], cms, changed_data) is True
    ), f"ERROR!.. Dos not updated with {contact} change: {changed_data}"


@then("the Changed Request with changed specified date and time is captured by Dos")
def the_changed_opening_time_is_accepted_by_dos(context):
    """assert dos API response and validate processed record in Dos CR Queue database"""
    open_time = time_to_sec(context["change_event"]["OpeningTimes"][-1]["OpeningTime"])
    closing_time = time_to_sec(context["change_event"]["OpeningTimes"][-1]["ClosingTime"])
    changed_time = f"{open_time}-{closing_time}"
    changed_date = context["change_event"]["OpeningTimes"][-1]["AdditionalOpeningDate"]
    cms = "cmsopentimespecified"
    approver_status = confirm_approver_status(context["correlation_id"])
    assert approver_status != [], f'Error!.. Dos Change for correlation id: {context["correlation_id"]} not COMPLETED'
    assert (
        check_specified_received_opening_times_date_in_dos(context["correlation_id"], cms, changed_date) is True
    ), f"ERROR!.. Dos not updated with change: {changed_date}"
    assert (
        check_specified_received_opening_times_time_in_dos(context["correlation_id"], cms, changed_time) is True
    ), f"ERROR!.. Dos not updated with change: {changed_time}"
    return context


@then("the Changed Request with changed standard day time is captured by Dos")
def the_changed_opening_standard_time_is_accepted_by_dos(context):
    """assert dos API response and validate processed record in Dos CR Queue database"""
    open_time = time_to_sec(context["change_event"]["OpeningTimes"][-2]["OpeningTime"])
    closing_time = time_to_sec(context["change_event"]["OpeningTimes"][-2]["ClosingTime"])
    changed_time = f"{open_time}-{closing_time}"
    cms = "cmsopentimemonday"
    assert (
        check_standard_received_opening_times_time_in_dos(context["correlation_id"], cms, changed_time) is True
    ), f"ERROR!.. Dos not updated with change: {changed_time}"


@then("the Changed Request with changed address is captured by Dos")
def the_changed_address_is_accepted_by_dos(context):
    """assert dos API response and validate processed record in Dos CR Queue database"""
    changed_address = context["change_event"]["Address1"]
    assert (
        check_received_data_in_dos(context["correlation_id"], "postaladdress", changed_address) is True
    ), f"ERROR!.. Dos not updated with address change: {changed_address}"


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
        ' | filter report_key="CR_DLQ_HANDLER_RECEIVED_EVENT"'
    )
    logs = get_logs(query, "cr_dlq", context["start_time"])
    assert "Change Request DLQ Handler hit" in logs, "ERROR!!.. expected exception logs not found."
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


@then("the date for the specified opening time returns an empty list")
def specified_opening_date_closed(context):
    closed_date = context["change_event"]["OpeningTimes"][-1]["AdditionalOpeningDate"]
    date_obj = dt.strptime(closed_date, "%b %d %Y").strftime("%Y-%m-%d")
    query = f'fields @message | sort @timestamp asc | filter correlation_id="{context["correlation_id"]}"'
    logs = get_logs(query, "sender", context["start_time"])
    assert f'\\"{date_obj}\\":[]' in logs, f"Expected closed date '{closed_date}' not captured"
    return context


@then("the day for the standard opening time returns an empty list")
def standard_opening_day_closed(context):
    closed_day = context["change_event"]["OpeningTimes"][-2]["Weekday"]
    query = f'fields @message | sort @timestamp asc | filter correlation_id="{context["correlation_id"]}"'
    logs = get_logs(query, "sender", context["start_time"])
    assert f'\\"{closed_day}\\":[]' in logs, f"Expected closed day '{closed_day}' not captured"
    return context


@then("the stored Changed Event is reprocessed in DI")
def replaying_changed_event(context):
    response = re_process_payload(context["change_event"]["ODSCode"], context["sequence_no"])
    assert (
        "The change event has been re-sent successfully" in response
    ), f"Error!.. Failed to re-process Change event. Message: {response}"
    context["correlation_id"] = ast.literal_eval(loads(response)).get("correlation_id")
    return context


@then("the reprocessed Changed Event is sent to Dos")
def verify_replayed_changed_event(context):
    response = confirm_changes(context["correlation_id"])
    assert response != [], "Error!.. Re-processed change event not found in Dos"


@then("the event processor logs should record a sequence error")
def sequence_id_error_logs(context):
    query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context["correlation_id"]}"'
        ' | filter message like "Sequence id is smaller than the existing one"'
    )
    logs = get_logs(query, "processor", context["start_time"])
    assert logs != [], "ERROR!!.. Sequence id error message not found."


@then("an invalid opening times error is generated")
def invalid_opening_times_error(context):
    query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context["correlation_id"]}"'
        ' | filter report_key like "INVALID_OPEN_TIMES"'
    )
    logs = get_logs(query, "processor", context["start_time"])
    assert "misformatted or illogical set of opening times." in logs, "ERROR!!.. error message not found."


@then("the opening times changes are confirmed valid")
def no_opening_times_errors(context):
    response = confirm_changes(context["correlation_id"])
    assert "cmsopentime" in str(response), "Error!.. Opening time Change not found in Dos Changes"


@then("the Changed Request with special characters is accepted by DOS")
def the_changed_website_is_accepted_by_dos(context):
    #   the test env uses a 'prod-like' DOS endpoint which rejects these
    current_env = getenv("ENVIRONMENT")
    if "test" in current_env:
        query = (
            "fields response_status_code | sort @timestamp asc"
            f' | filter correlation_id="{context["correlation_id"]}"'
            ' | filter message like "Failed to send change request to DoS"'
        )
        logs = get_logs(query, "sender", context["start_time"])
        assert "400" in logs, "ERROR!!.. 400 response not received from DOS"
    else:
        #       the mock DOS currently accepts the invalid characters
        uri_timestamp = context["uri_timestamp"]
        complete_uri = f"https:\\\\/\\\\/www.rowlandspharmacy.co.uk\\\\/test?foo={uri_timestamp}"  # noqa: W605
        query = (
            "fields change_request_body.changes.website | sort @timestamp asc"
            f' | filter correlation_id="{context["correlation_id"]}"'
            ' | filter message like "Attempting to send change request to DoS"'
        )
        logs = get_logs(query, "sender", context["start_time"])
        assert complete_uri in logs, "ERROR!!.. website not found in CR."
        successquery = (
            f'fields message | sort @timestamp asc | filter correlation_id="{context["correlation_id"]}"'
            ' | filter message like "Successfully send change request to DoS"'
        )
        logs = get_logs(successquery, "sender", context["start_time"])
        assert logs != [], "ERROR!!.. successful log messages not showing in cloudwatch."


@then("the Changed Event is replayed with the specified opening date deleted")
def change_event_is_replayed(context, valid_or_invalid):
    target_date = context["change_event"]["OpeningTimes"][-1]["AdditionalOpeningDate"]
    del context["change_event"]["OpeningTimes"][-1]
    context["correlation_id"] = f'{context["correlation_id"]}-replay'
    context["response"] = process_payload(
        context["change_event"], valid_or_invalid == "valid", context["correlation_id"]
    )
    context["change_event"]["deleted_date"] = target_date
    return context


@then("the deleted specified date is confirmed removed from Dos")
def specified_date_is_removed_from_dos(context):
    service_id = get_service_id(context["correlation_id"])
    removed_date = dt.strptime(context["change_event"]["deleted_date"], "%b %d %Y").strftime("%y-%m-%d")
    approver_status = confirm_approver_status(context["correlation_id"])
    assert approver_status != [], f"Error!.. Dos Change for Serviceid: {service_id} has been REJECTED"
    specified_opening_times_from_db = get_change_event_specified_opening_times(service_id)
    assert removed_date not in str(
        specified_opening_times_from_db
    ), f"Error!.. Removed specified date: {removed_date} still exists in Dos"


@then(parsers.parse('the Changed Event is replayed with the pharmacy now "{open_or_closed}"'))
def event_replayed_with_pharmacy_closed(context, valid_or_invalid, open_or_closed):
    closing_time = datetime.datetime.now().time().strftime("%H:%M")
    if open_or_closed.upper() == "OPEN":
        context["change_event"]["OpeningTimes"][-2]["OpeningTime"] = "00:01"
        context["change_event"]["OpeningTimes"][-2]["ClosingTime"] = closing_time
        context["change_event"]["OpeningTimes"][-2]["IsOpen"] = True
        context["correlation_id"] = f'{context["correlation_id"]}_open_replay'
    elif open_or_closed.upper() == "CLOSED":
        context["change_event"]["OpeningTimes"][-2]["OpeningTime"] = ""
        context["change_event"]["OpeningTimes"][-2]["ClosingTime"] = ""
        context["change_event"]["OpeningTimes"][-2]["IsOpen"] = False
        context["correlation_id"] = f'{context["correlation_id"]}_closed_replay'
    else:
        raise ValueError(f'Invalid status input parameter: "{open_or_closed}"')
    context["response"] = process_payload(
        context["change_event"], valid_or_invalid == "valid", context["correlation_id"]
    )
    return context


@then(parsers.parse('the pharmacy is confirmed "{open_or_closed}" for the standard day in Dos'))
def standard_day_confirmed_open(context, open_or_closed):
    approver_status = confirm_approver_status(context["correlation_id"])
    assert approver_status != [], "Error!.. Dos Change not Approved or COMPLETED"
    service_id = get_service_id(context["correlation_id"])
    opening_time_event = get_change_event_standard_opening_times(service_id)
    week_day = context["change_event"]["OpeningTimes"][-2]["Weekday"]
    if open_or_closed.upper() == "CLOSED":
        assert (
            opening_time_event[week_day] == []
        ), f'ERROR!.. Pharmacy is CLOSED but expected to be OPEN for "{week_day}"'
    elif open_or_closed.upper() == "OPEN":
        assert (
            opening_time_event[week_day] != []
        ), f'ERROR!.. Pharmacy is OPEN but expected to be CLOSED for "{week_day}"'
    else:
        raise ValueError(f'Invalid status input parameter: "{open_or_closed}"')
    return context


@then("the Dentist changes with service type id is captured by Dos")
def dentist_changes_confirmed_in_dos(context):
    change_event_service_type = get_service_type_data(context["change_event"]["OrganisationTypeId"])[
        "VALID_SERVICE_TYPES"
    ]
    change_request_service_type = get_service_type_from_cr(context["correlation_id"])
    assert change_event_service_type[0] == change_request_service_type, "ERROR!.. Service type id mismatch"
