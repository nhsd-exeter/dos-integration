import ast
from datetime import datetime as dt
from decimal import Decimal
from json import loads
from os import environ, getenv
from random import randint
from time import sleep

from faker import Faker
from pytest_bdd import given, scenarios, then, when
from pytest_bdd.parsers import parse
from .utilities.cloudwatch import get_logs, negative_log_check
from .utilities.context import Context
from .utilities.translation import get_service_table_field_name
from .utilities.utils import (
    assert_standard_closing,
    assert_standard_openings,
    check_pending_service_is_rejected,
    check_service_history,
    check_service_history_change_type,
    convert_specified_opening,
    convert_standard_opening,
    create_pending_change_for_service,
    generate_correlation_id,
    generate_random_int,
    get_address_string,
    get_change_event_specified_opening_times,
    get_change_event_standard_opening_times,
    get_expected_data,
    get_latest_sequence_id_for_a_given_odscode,
    get_locations_table_data,
    get_s3_email_file,
    get_service_history,
    get_service_history_specified_opening_times,
    get_service_history_standard_opening_times,
    get_service_id,
    get_service_table_field,
    get_services_table_location_data,
    get_stored_events_from_dynamo_db,
    post_to_change_event_dlq,
    post_ur_fifo,
    post_ur_sqs,
    process_payload,
    process_payload_with_sequence,
    re_process_payload,
    service_history_negative_check,
    slack_retry,
    wait_for_service_update,
)
from .utilities.generator import (
    add_single_opening_day,
    add_specified_openings_to_dos,
    add_standard_openings_to_dos,
    build_change_event,
    build_change_event_contacts,
    build_change_event_opening_times,
    commit_new_service_to_dos,
    create_palliative_care_entry_ce,
    create_palliative_care_entry_dos,
    generate_staff,
    query_specified_opening_builder,
    query_standard_opening_builder,
    valid_change_event,
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


@given(parse('the "{contact}" is changed and is valid'), target_fixture="context")
def a_changed_contact_event_is_valid(contact: str, context: Context):
    validated = False
    while not validated:
        match contact.lower():
            case "website":
                context.previous_value = context.website
                context.website = FAKER.domain_word() + ".nhs.uk"
                context.generator_data["web"] = context.website
                context.change_event["Contacts"] = build_change_event_contacts(context)
            case "phone_no":
                context.previous_value = context.phone
                context.phone = FAKER.phone_number()
                context.generator_data["publicphone"] = context.phone
                context.change_event["Contacts"] = build_change_event_contacts(context)
            case "address":
                context.previous_value = get_address_string(context)
                context.change_event["Address1"] = FAKER.street_name()
            case _:
                raise ValueError(f"ERROR!.. Input parameter '{contact}' not compatible")
        validated = valid_change_event(context)
    return context


@given("an entry is created in the services table", target_fixture="context")
def a_service_table_entry_is_created(context: Context):
    ods_code = str(randint(10000, 99999))
    query_values = {
        "id": str(randint(100000, 999999)),
        "uid": f"test{str(randint(10000,99999))}",
        "service_type": 13,
        "service_status": 1,
        "name": f"Test Pharmacy {str(randint(100,999))}",
        "odscode": ods_code,
        "address": f"{str(randint(100,999))} Test Address",
        "town": "Nottingham",
        "postcode": "NG11GS",
        "publicphone": f"{str(randint(10000000000, 99999999999))}",
        "web": "www.google.com",
        "palliative": False
    }
    context.generator_data = query_values
    return context

@given("the service in DoS supports palliative care", target_fixture="context")
def add_palliative_care_to_dos(context: Context):
    pal_id = create_palliative_care_entry_dos(context)
    context.other = pal_id
    return context


@given("the change event has a palliative care entry", target_fixture="context")
def add_palliative_care_to_ce(context: Context):
    create_palliative_care_entry_ce(context)
    return context


@given("a basic service is created", target_fixture="context")
def create_basic_service_entry(context: Context):
    context = a_service_table_entry_is_created(context)
    context = service_table_entry_is_committed(context)
    return context


@given(parse('the service "{field_name}" is set to "{values}"'), target_fixture="context")
def service_values_updated_in_context(field_name: str, values: str, context: Context):
    context.generator_data[field_name] = values
    return context


@given(parse('the service is "{service_status}" on "{day}"'), target_fixture="context")
def service_standard_opening_set(service_status: str, day: str, context: Context):
    if day.lower() not in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
        raise ValueError("Selected day is not valid")
    query_standard_opening_builder(context, service_status, day)
    return context


@given(parse('the change event is "{service_status}" on "{day}"'), target_fixture="context")
def change_event_standard_opening_set(service_status: str, day: str, context: Context):
    if day.lower() not in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
        raise ValueError("Selected day is not valid")
    query_standard_opening_builder(context, service_status, day)
    context.change_event["OpeningTimes"] = build_change_event_opening_times(context)
    # standard_openings: [{day: "Monday", open: True, opening_time: "09:00", closing_time: "17:00"}]
    return context


@given(parse('the service is "{service_status}" on date "{date}"'), target_fixture="context")
def service_specified_opening_set(service_status: str, date: str, context: Context):
    query_specified_opening_builder(context, service_status, date)
    return context


@given(parse('the change event is "{service_status}" on date "{date}"'), target_fixture="context")
def change_event_specified_opening_set(service_status: str, date: str, context: Context):
    query_specified_opening_builder(context, service_status, date)
    context.change_event["OpeningTimes"] = build_change_event_opening_times(context)
    return context


@given(
    parse('the change event is "{service_status}" from "{open}" to "{close}" on date "{date}"'),
    target_fixture="context",
)
def change_event_specified_opening_set_times(service_status: str, date: str, open: str, close: str, context: Context):
    query_specified_opening_builder(context, service_status, date, open, close)
    context.change_event["OpeningTimes"] = build_change_event_opening_times(context)
    return context


@given("the change event has no specified opening dates", target_fixture="context")
def change_event_no_specified_opening_dates(context: Context):
    date_vals = context.generator_data["specified_openings"][0]
    context.other = {
        "AdditionalOpeningDate": date_vals["date"],
        "OpeningTime": date_vals["opening_time"],
        "ClosingTime": date_vals["closing_time"],
    }
    context.generator_data["specified_openings"] = []
    context.change_event["OpeningTimes"] = build_change_event_opening_times(context)
    return context


@given("the entry is committed to the services table", target_fixture="context")
def service_table_entry_is_committed(context: Context):
    service_id = commit_new_service_to_dos(context)
    context.service_id = service_id
    ce_state = False
    if "standard_openings" in context.generator_data.keys():
        add_standard_openings_to_dos(context)
        ce_state = True
    if "specified_openings" in context.generator_data.keys():
        add_specified_openings_to_dos(context)
    if context.change_event is None:
        build_change_event(context)
    if ce_state:
        context.change_event["OpeningTimes"] = build_change_event_opening_times(context)
    else:
        add_single_opening_day(context)
        context.change_event["OpeningTimes"] = build_change_event_opening_times(context)
    return context


@given(parse('the change event "{field_name}" is set to "{values}"'), target_fixture="context")
def ce_values_updated_in_context(field_name: str, values: str, context: Context):
    if field_name.lower() == "website":
        context.previous_value = context.generator_data["web"]
        context.generator_data["web"] = values
        context.change_event["Contacts"] = build_change_event_contacts(context)
    elif field_name.lower() == "phone":
        context.previous_value = context.generator_data["publicphone"]
        context.generator_data["publicphone"] = values
        context.change_event["Contacts"] = build_change_event_contacts(context)
    else:
        context.previous_value = context.change_event[field_name]
        context.change_event[field_name] = values
    return context


@given("the change event staff field is populated", target_fixture="context")
def ce_staff_field_populated(context: Context):
    context.change_event["Staff"] = generate_staff()
    return context


@given("the change event has no staff field", target_fixture="context")
def ce_staff_field_removed(context: Context):
    del context.change_event["Staff"]
    return context


@given(parse('the specified opening date is set to "{future_past}" date'), target_fixture="context")
def future_set_specified_opening_date(future_past: str, context: Context):
    year = 0
    if future_past.lower() == "future":
        year = dt.now().year + 1
        context.change_event["OpeningTimes"].append(
            {
                "Weekday": "",
                "OpeningTime": "08:00",
                "ClosingTime": "16:00",
                "OffsetOpeningTime": 0,
                "OffsetClosingTime": 0,
                "OpeningTimeType": "Additional",
                "AdditionalOpeningDate": f"Jan 10 {year}",
                "IsOpen": True,
            }
        )
    else:
        for days in context.change_event["OpeningTimes"]:
            if days["OpeningTimeType"] == "Additional":
                context.change_event["OpeningTimes"].remove(days)
    return context


@given("a pending entry exists in the changes table for this service", target_fixture="context")
def change_table_entry_creation_for_service(context: Context):
    service_id = context.generator_data["id"]
    service_uid = context.generator_data["uid"]
    context.service_uid = service_uid
    create_pending_change_for_service(service_id)
    return context


@given(parse('the "{contact}" value has been unset'), target_fixture="context")
def changed_event_contact_removed(contact: str, context: Context):
    match contact.lower():
        case "website":
            context.previous_value = context.generator_data["web"]
            context.generator_data["web"] = None
            context.change_event["Contacts"] = build_change_event_contacts(context)
        case "phone":
            context.previous_value = context.generator_data["publicphone"]
            context.generator_data["publicphone"] = None
            context.change_event["Contacts"] = build_change_event_contacts(context)
        case _:
            raise ValueError(f"Invalid contact '{contact}' provided")
    return context


@given(parse('the Changed Event has "{amount}" break in opening times'), target_fixture="context")
def change_event_with_break_in_opening_times(context: Context, amount):
    context.generator_data["standard_openings"] = []
    if amount in ["1", "2", "3"]:
        query_standard_opening_builder(context, "open", "monday", "09:00", "12:00")
        query_standard_opening_builder(context, "open", "monday", "12:30", "16:00")
    if amount in ["2", "3"]:
        query_standard_opening_builder(context, "open", "monday", "16:10", "16:30")
    if amount in ["3"]:
        query_standard_opening_builder(context, "open", "monday", "16:40", "17:00")
    context.change_event["OpeningTimes"] = build_change_event_opening_times(context)
    return context


# Weekday NOT present on the Opening Time
@given("the change event has no weekday present in opening times", target_fixture="context")
def a_change_event_with_no_openingtimes_weekday(context: Context):
    del context.change_event["OpeningTimes"][0]["Weekday"]
    return context


# OpeningTimeType is NOT "General" or "Additional"
@given("the change event has an invalid openingtimetype", target_fixture="context")
def a_change_event_with_invalid_openingtimetype(context: Context):
    context.change_event["OpeningTimes"][0]["OpeningTimeType"] = "F8k3"
    return context


# IsOpen is true AND Times is blank
@given("the change event has undefined opening and closing times", target_fixture="context")
def no_times_data_within_openingtimes(context: Context):
    context.change_event["OpeningTimes"][0]["OpeningTime"] = ""
    context.change_event["OpeningTimes"][0]["ClosingTime"] = ""
    return context


# isOpen is false AND Times in NOT blank
@given("the change event has opening times open status set to false", target_fixture="context")
def a_change_event_with_isopen_status_set_to_false(context: Context):
    context.change_event["OpeningTimes"][0]["IsOpen"] = False
    return context


# OpeningTimeType is Additional AND AdditionalOpening Date is Blank
@given("the change event has an additional date with no specified date", target_fixture="context")
def specified_opening_date_not_defined(context: Context):
    context.change_event["OpeningTimes"].append(
        {
            "AdditionalOpeningDate": "",
            "ClosingTime": "12:00",
            "IsOpen": True,
            "OffsetClosingTime": 780,
            "OffsetOpeningTime": 540,
            "OpeningTime": "09:00",
            "OpeningTimeType": "Additional",
            "Weekday": "",
        }
    )
    return context


@given(parse('the correlation-id is "{custom_correlation}"'), target_fixture="context")
def a_custom_correlation_id_is_set(context: Context, custom_correlation: str):
    context.correlation_id = generate_correlation_id(custom_correlation)
    return context


@given("the ODS has an entry in dynamodb", target_fixture="context")
def create_ods_in_ddb(context: Context):
    context = the_change_event_is_sent_with_custom_sequence(context, 100)
    context.sequence_number = 100
    context.unique_key = generate_random_int()
    return context


@when(parse('a "{queue_type}" SQS message is added to the queue'), target_fixture="context")
def post_an_sqs_message(queue_type: str, context: Context):
    match queue_type.lower():
        case "change event dlq":
            post_to_change_event_dlq(context)
        case "update request dlq":
            post_ur_sqs()
        case "update request failure":
            post_ur_fifo()
        case _:
            raise ValueError(f"ERROR!.. queue type '{queue_type}' is not valid")


@when(
    parse('the Changed Event is sent for processing with "{valid_or_invalid}" api key'),
    target_fixture="context",
)
def the_change_event_is_sent_for_processing(context: Context, valid_or_invalid):
    if context.phone is not None or context.website is not None:
        context.change_event["Contacts"] = build_change_event_contacts(context)
    context.start_time = dt.today().timestamp()
    context.correlation_id = generate_correlation_id()
    context.response = process_payload(context, valid_or_invalid == "valid", context.correlation_id)
    context.sequence_number = context.response.request.headers["sequence-number"]
    return context


# Request with custom sequence id
@when(
    parse('the Changed Event is sent for processing with sequence id "{seqid}"'),
    target_fixture="context",
)
def the_change_event_is_sent_with_custom_sequence(context: Context, seqid):
    context.start_time = dt.today().timestamp()
    context.correlation_id = generate_correlation_id()
    context.response = process_payload_with_sequence(context, context.correlation_id, seqid)
    context.sequence_number = seqid
    return context


# Request with no sequence id
@when(
    parse("the Changed Event is sent for processing with no sequence id"),
    target_fixture="context",
)
def the_change_event_is_sent_with_no_sequence(context: Context):
    context.start_time = dt.today().timestamp()
    context.correlation_id = generate_correlation_id()
    context.response = process_payload_with_sequence(context, context.correlation_id, None)
    return context


# Request with duplicate sequence id
@when(
    parse("the Changed Event is sent for processing with a duplicate sequence id"),
    target_fixture="context",
)
def the_change_event_is_sent_with_duplicate_sequence(context: Context):
    context.start_time = dt.today().timestamp()
    context.correlation_id = generate_correlation_id()
    context.change_event["Address1"] = "New Test Address Value"
    seqid = 0
    if context.sequence_number == 100:
        seqid = 100
    else:
        seqid = get_latest_sequence_id_for_a_given_odscode(context.ods_code)
    context.response = process_payload_with_sequence(context, context.correlation_id, seqid)
    context.sequence_number = seqid
    return context


@then("the Changed Event is stored in dynamo db")
def stored_dynamo_db_events_are_pulled(context: Context):
    odscode = context.change_event["ODSCode"]
    sequence_num = Decimal(context.sequence_number)
    sleep(15)
    db_event_record = get_stored_events_from_dynamo_db(odscode, sequence_num)
    assert db_event_record is not None, f"ERROR!! Event record with odscode {odscode} NOT found!.."
    assert (
        odscode == db_event_record["ODSCode"]
    ), f"ERROR!!.. Change event record({odscode} - {db_event_record['ODSCode']}) mismatch!!"
    assert sequence_num == db_event_record["SequenceNumber"], "ERROR!!.. Change event record(sequence no) mismatch!!"
    return context


@then(parse('the "{plain_english_service_table_field}" has not been changed in DoS'))
def field_is_not_updated_in_dos(context: Context, plain_english_service_table_field: str):
    sleep(60)
    field_name = get_service_table_field_name(plain_english_service_table_field)
    field_data = get_service_table_field(service_id=context.service_id, field_name=field_name)
    assert (
        context.previous_value in field_data
    ), f"ERROR!.. DoS doesn't have expected {plain_english_service_table_field} data - It has changed from expected value, expected: {context.previous_value}, actual: {field_data}"  # noqa: E501


@then(parse('DoS has "{expected_data}" in the "{plain_english_service_table_field}" field'))
def expected_data_is_within_dos(context: Context, expected_data: str, plain_english_service_table_field: str):
    """Assert DoS demographics data is updated"""
    wait_for_service_update(context.service_id)
    field_name = get_service_table_field_name(plain_english_service_table_field)
    field_data = get_service_table_field(service_id=context.service_id, field_name=field_name)
    if plain_english_service_table_field in ["easting", "northing"]:
        expected_data = int(expected_data)
    elif plain_english_service_table_field in ["latitude", "longitude"]:
        expected_data = float(expected_data)
    assert (
        field_data == expected_data
    ), f"ERROR!.. DoS doesn't have expected {plain_english_service_table_field} data, expected: {expected_data}, actual: {field_data}"  # noqa: E501


@then(parse('the "{plain_english_service_table_field}" is updated within the DoS DB'))
def check_the_service_table_field_has_updated(context: Context, plain_english_service_table_field: str):
    """TODO"""
    wait_for_service_update(context.service_id)
    field_name = get_service_table_field_name(plain_english_service_table_field)
    field_data = get_service_table_field(service_id=context.service_id, field_name=field_name)
    expected_value = get_expected_data(context, plain_english_service_table_field)
    expected_value = expected_value if expected_value is not None else ""
    assert field_data == expected_value, (
        f"ERROR!!.. Expected {plain_english_service_table_field} not found in Dos DB., "
        f"expected: {expected_value}, found: {field_data}"
    )
    return context


@then(parse('the service history is updated with the "{plain_english_service_table_field}"'))
def check_the_service_history_has_updated(context: Context, plain_english_service_table_field: str):
    """TODO"""
    expected_data = get_expected_data(context, plain_english_service_table_field)
    if context.previous_value in ["", "unknown"]:
        context.previous_value = "unknown"
    check_service_history(
        service_id=context.service_id,
        plain_english_field_name=plain_english_service_table_field,
        expected_data=expected_data,
        previous_data=context.previous_value,
    )
    return context


@then(parse('the service history is updated with the "{added_or_removed}" specified opening times'))
def check_service_history_specified_times(context: Context, added_or_removed):
    match added_or_removed:
        case "added":
            change_type = "add"
        case "removed":
            change_type = "remove"
        case "closed":
            change_type = "add"
        case _:
            raise ValueError("Invalid change type has been provided")
    if change_type == "add":
        openingtimes = context.change_event["OpeningTimes"][-1]
    if change_type == "remove":
        openingtimes = context.other
    dos_times = get_service_history_specified_opening_times(context.service_id)
    changed_dates = dos_times["data"][change_type]
    if added_or_removed == "closed":
        expected_dates = convert_specified_opening(openingtimes, True)
    else:
        expected_dates = convert_specified_opening(openingtimes)
    assert expected_dates in changed_dates, f"{expected_dates}"
    return context


@then(parse('the service history is updated with the "{added_or_removed}" standard opening times'))
def check_service_history_standard_times(context: Context, added_or_removed):
    sleep(10)
    openingtimes = context.change_event["OpeningTimes"]
    dos_times = get_service_history_standard_opening_times(context.service_id)
    expected_dates = convert_standard_opening(openingtimes)
    counter = 0
    strict_checks = False
    if "f006s012" in environ.get("PYTEST_CURRENT_TEST"):
        strict_checks = True
    if added_or_removed == "added":
        counter = assert_standard_openings("add", dos_times, expected_dates, strict_checks)
    elif added_or_removed == "modified":
        counter = assert_standard_openings("modify", dos_times, expected_dates, strict_checks)
    else:
        counter = assert_standard_closing(dos_times, expected_dates)
    if counter == 0:
        raise ValueError("ERROR: No Assertions have been made")
    return context


@then(parse("the service history is not updated"))
def check_service_history_not_updated(
    context: Context,
):
    service_history_status = service_history_negative_check(context.service_id)
    assert service_history_status == "Not Updated", "ERROR: Service history was unexpectedly updated"
    return context


@then(parse('the service history shows change type is "{change_type}"'))
def check_service_history_for_change_type(context: Context, change_type: str):
    # This brings instability if more than one entry has been changed
    change_status = check_service_history_change_type(context.service_id, change_type)
    assert change_status == "Change type matches", f"ERROR: Expected {change_type} but {change_status}"
    return context


@then(parse('the service history shows "{field_name}" change type is "{change_type}"'))
def check_service_history_for_specific_change_type(context: Context, change_type: str, field_name: str):
    change_status = check_service_history_change_type(context.service_id, change_type, field_name)
    assert change_status == "Change type matches", f"ERROR: Expected {change_type} but {change_status}"
    return context


@then("the DoS service has been updated with the specified date and time is captured by DoS")
def the_dos_service_has_been_updated_with_the_specified_date_and_time_is_captured_by_dos(context: Context):
    context.service_id = get_service_id(context.change_event["ODSCode"])
    wait_for_service_update(context.service_id)
    opening_time = context.change_event["OpeningTimes"][-1]["OpeningTime"]
    closing_time = context.change_event["OpeningTimes"][-1]["ClosingTime"]
    changed_date = context.change_event["OpeningTimes"][-1]["AdditionalOpeningDate"]
    current_specified_openings = get_change_event_specified_opening_times(context.service_id)
    expected_opening_date = dt.strptime(changed_date, "%b %d %Y").strftime("%Y-%m-%d")
    assert expected_opening_date in current_specified_openings, "DoS not updated with specified opening time"
    assert current_specified_openings[expected_opening_date][0]["start_time"] == opening_time
    assert current_specified_openings[expected_opening_date][0]["end_time"] == closing_time


@then(parse('the DoS DB has no open date in "{year}"'))
def the_dos_service_has_no_past_openings(context: Context, year: str):
    wait_for_service_update(context.generator_data["id"])
    current_specified_openings = get_change_event_specified_opening_times(context.generator_data["id"])
    if current_specified_openings == {}:
        assert True
    else:
        assert year not in current_specified_openings, f"{year} not found in {current_specified_openings}"


@then("the DoS service has been updated with the standard days and times is captured by DoS")
def the_dos_service_has_been_updated_with_the_standard_days_and_times_is_captured_by_dos(context: Context):
    context.service_id = get_service_id(context.change_event["ODSCode"])
    wait_for_service_update(context.service_id)
    open_time = context.change_event["OpeningTimes"][0]["OpeningTime"]
    closing_time = context.change_event["OpeningTimes"][0]["ClosingTime"]
    current_standard_openings = get_change_event_standard_opening_times(context.service_id)
    assert "Monday" in current_standard_openings, "DoS not updated with standard opening time"
    assert current_standard_openings["Monday"][0]["start_time"] == open_time
    assert current_standard_openings["Monday"][0]["end_time"] == closing_time


@then(parse('the change event response has status code "{status}"'))
def step_then_should_transform_into(context: Context, status):
    message = context.response.json
    assert (
        str(context.response.status_code) == status
    ), f"Status code not as expected: {context.response.status_code} != {status} Error: {message} - {status}"


@then("the attributes for invalid opening times report is identified in the logs")
def invalid_opening_times_exception(context: Context):
    query = (
        f'fields @message | sort @timestamp asc | filter correlation_id="{context.correlation_id}"'
        '| filter report_key="INVALID_OPEN_TIMES"'
    )
    logs = get_logs(query, "service-matcher", context.start_time)
    for item in [
        "nhsuk_odscode",
        "nhsuk_organisation_name",
        "nhsuk_open_times_payload",
        "dos_services",
    ]:
        assert item in logs


@then("the stored Changed Event is reprocessed in DI")
def replaying_changed_event(context: Context):
    response = re_process_payload(context.change_event["ODSCode"], context.sequence_number)
    assert (
        "The change event has been re-sent successfully" in response
    ), f"Error!.. Failed to re-process Change event. Message: {response}"
    context.correlation_id = ast.literal_eval(loads(response)).get("correlation_id")
    return context


@then("opening times with a break are updated in DoS")
def opening_times_with_a_break_are_updated_in_dos(context: Context):
    context.service_id = get_service_id(context.change_event["ODSCode"])
    wait_for_service_update(context.service_id)
    current_standard_openings = get_change_event_standard_opening_times(context.service_id)
    assert "Monday" in current_standard_openings, "DoS not updated with standard opening time"
    assert current_standard_openings["Monday"][0]["start_time"] == "09:00"
    assert current_standard_openings["Monday"][0]["end_time"] == "12:00"
    assert current_standard_openings["Monday"][1]["start_time"] == "12:30"
    assert current_standard_openings["Monday"][1]["end_time"] == "16:00"
    assert len(current_standard_openings["Monday"]) == 2, "Expected 2 opening times"


@then("opening times with two breaks are updated in DoS")
def opening_times_with_two_breaks_are_updated_in_dos(context: Context):
    context.service_id = get_service_id(context.change_event["ODSCode"])
    wait_for_service_update(context.service_id)
    current_standard_openings = get_change_event_standard_opening_times(context.service_id)
    assert "Monday" in current_standard_openings, "DoS not updated with standard opening time"
    assert current_standard_openings["Monday"][0]["start_time"] == "09:00"
    assert current_standard_openings["Monday"][0]["end_time"] == "12:00"
    assert current_standard_openings["Monday"][1]["start_time"] == "12:30"
    assert current_standard_openings["Monday"][1]["end_time"] == "16:00"
    assert current_standard_openings["Monday"][2]["start_time"] == "16:10"
    assert current_standard_openings["Monday"][2]["end_time"] == "16:30"
    assert len(current_standard_openings["Monday"]) == 3, "Expected 3 opening times"


@then(parse('DoS is open on "{date}"'), target_fixture="context")
def the_changed_opening_time_is_accepted_by_dos(context: Context, date):
    wait_for_service_update(context.generator_data["id"])
    current_specified_openings = get_change_event_specified_opening_times(context.generator_data["id"])
    expected_opening_date = dt.strptime(date, "%b %d %Y").strftime("%Y-%m-%d")
    assert expected_opening_date in current_specified_openings, "DoS not updated with specified opening time"
    assert current_specified_openings[expected_opening_date] != [], "Date is not open in DoS"
    return context


@then(parse('DoS is open from "{open}" until "{close}" on "{date}"'), target_fixture="context")
def the_changed_opening_time_is_accepted_by_dos_specific(context: Context, date, open, close):
    wait_for_service_update(context.generator_data["id"])
    current_specified_openings = get_change_event_specified_opening_times(context.generator_data["id"])
    expected_opening_date = dt.strptime(date, "%b %d %Y").strftime("%Y-%m-%d")
    assert expected_opening_date in current_specified_openings, "DoS not updated with specified opening time"
    assert (
        current_specified_openings[expected_opening_date][0]["start_time"] == open
    ), "Date is not open at correct times"
    assert (
        current_specified_openings[expected_opening_date][0]["end_time"] == close
    ), "Date is not closed at correct times"
    return context


@then(parse('DoS is closed on "{date}"'), target_fixture="context")
def the_changed_closing_time_is_accepted_by_dos(context: Context, date):
    wait_for_service_update(context.generator_data["id"])
    current_specified_openings = get_change_event_specified_opening_times(context.generator_data["id"])
    expected_opening_date = dt.strptime(date, "%b %d %Y").strftime("%Y-%m-%d")
    assert expected_opening_date in current_specified_openings, "DoS not updated with specified opening time"
    assert current_specified_openings[expected_opening_date] == [], "Date is not closed in DoS"
    return context


@then(parse('there is no longer a specified opening on "{date}"'), target_fixture="context")
def specified_date_is_removed_from_dos(context: Context, date):
    sleep(60)
    current_specified_openings = get_change_event_specified_opening_times(context.generator_data["id"])
    expected_opening_date = dt.strptime(date, "%b %d %Y").strftime("%Y-%m-%d")
    assert (
        expected_opening_date not in current_specified_openings
    ), f"Specified date {expected_opening_date} not removed from DoS"
    return context


@then(parse('the pharmacy is confirmed "{open_or_closed}" on "{day}"'), target_fixture="context")
def standard_day_confirmed_open_check(context: Context, open_or_closed: str, day: str):
    context.service_id = context.generator_data["id"]
    sleep(60)
    opening_time_event = get_change_event_standard_opening_times(context.service_id)
    match open_or_closed.upper():
        case "CLOSED":
            assert opening_time_event[day] == [], f'ERROR!.. Pharmacy is CLOSED but expected to be OPEN for "{day}"'
        case "OPEN":
            assert opening_time_event[day] != [], f'ERROR!.. Pharmacy is OPEN but expected to be CLOSED for "{day}"'
        case _:
            raise ValueError(f'Invalid status input parameter: "{open_or_closed}"')
    return context


@then(parse('the "{lambda_name}" lambda shows field "{field}" with message "{message}"'))
def generic_lambda_log_check_function(context: Context, lambda_name: str, field, message):
    if "/" in context.correlation_id:
        context.correlation_id = context.correlation_id.replace("/", r"\/")
    query = (
        f"fields {field} | sort @timestamp asc"
        f' | filter correlation_id="{context.correlation_id}" | filter {field} like "{message}"'
    )
    logs = get_logs(query, lambda_name, context.start_time)
    assert message in logs, f"ERROR!!.. error event processor did not detect the {field}: {message}."


@then(parse('the "{lambda_name}" lambda does not show "{field}" with message "{message}"'))
def generic_lambda_log_negative_check_function(context: Context, lambda_name: str, field, message):
    find_request_id_query = (
        "fields function_request_id | sort @timestamp asc" f' | filter correlation_id="{context.correlation_id}"'
    )
    find_request_id = loads(get_logs(find_request_id_query, lambda_name, context.start_time))

    request_id = ""
    for x in find_request_id["results"][0]:
        if x["field"] == "function_request_id":
            request_id = x["value"]

    finished_check = f'fields @message | filter @requestId == "{request_id}" | filter @type == "END"'

    get_logs(finished_check, lambda_name, context.start_time, 2)

    query = (
        f"fields {field} | sort @timestamp asc"
        f' | filter correlation_id="{context.correlation_id}" | filter {field} like "{message}"'
    )
    logs_found = negative_log_check(query, lambda_name, context.start_time)

    assert logs_found is True, f"ERROR!!.. error event processor did not detect the {field}: {message}."


@then(parse('the Slack channel shows an alert saying "{message}" from "{environment_type}"'))
def slack_message_check(message: str, environment_type: str):
    slack_entries = slack_retry(message)
    current_environment = getenv(environment_type)
    assert_string = f"{current_environment} | {message}"
    assert assert_string in slack_entries


@then("the service table has been updated with locations data")
def services_location_update_assertion(context: Context):
    sleep(20)
    location_data = get_locations_table_data(context.change_event["Postcode"])
    services_data = get_services_table_location_data(context.service_id)
    assert services_data == location_data, "ERROR: Services and Location data does not match"


@then("the service history table has been updated with locations data")
def services_location_history_update_assertion(context: Context):
    sleep(10)
    history_data = get_service_history(context.service_id)
    history_data = history_data[list(history_data.keys())[0]]["new"]
    history_list = []
    history_list.append(history_data["cmsorgtown"]["data"])
    history_list.append(history_data["postalcode"]["data"])
    history_list.append(history_data["cmseastings"]["data"])
    history_list.append(history_data["cmsnorthings"]["data"])
    location_data = get_locations_table_data(context.change_event["Postcode"])
    location_data = location_data[0][:-2]
    assert history_list == location_data, "ERROR: Service History and Location data does not match"


@then("the s3 bucket contains an email file matching the service uid")
def check_s3_contains_email_file(context: Context):
    get_s3_email_file(context)
    assert context.service_uid in context.other["email_body"], "ERROR: service_uid not found in email body"


@then("the changes table shows change is now rejected")
def check_changes_table_has_been_updated(context: Context):
    status = check_pending_service_is_rejected(context.service_id)
    assert "REJECTED" in status, "ERROR: changes table has not been updated"


@then("service sync log contains no overlapping log data", target_fixture="context")
def show_service_sync_logs(context: Context):
    query = (
        f'fields @message | sort @timestamp asc | filter correlation_id="{context.correlation_id}"'
        '|filter message like "Attempting connection to database"'
    )
    logs = loads(get_logs(query, "service-sync", context.start_time))["results"][0][0]["value"]
    assert "service_uid" and "service_name" not in logs, "ERROR: service uid and service name found in logs"


@then("logs show staff data has been redacted", target_fixture="context")
def ingest_staff_redaction(context: Context):
    query = "fields @message | sort @timestamp asc" '|filter message like "key from Change Event payload"'
    logs = loads(get_logs(query, "ingest-change-event", context.start_time))
    assert logs != [], "ERROR: Logs do not show redaction of staff field"
    return context


@then("error messages do not show Staff data", target_fixture="context")
def error_contains_no_staff(context: Context):
    query = (
        f'fields @event | sort @timestamp asc | filter correlation_id="{context.correlation_id}"'
        '|filter message like "Validation Error - Unexpected Org Sub Type ID"'
    )
    logs = loads(get_logs(query, "ingest-change-event", context.start_time))
    assert "Superintendent Pharmacist" not in logs, "ERROR: Logs output the staff field on error"
    return context
