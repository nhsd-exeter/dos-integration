import ast
from ast import literal_eval
from datetime import datetime as dt
from decimal import Decimal
from json import loads
from os import environ, getenv
from random import randint
from time import sleep

from faker import Faker
from pytest_bdd import given, scenarios, then, when
from pytest_bdd.parsers import parse
from pytz import timezone

from .functions.api import process_payload, process_payload_with_sequence
from .functions.assertions import assert_standard_closing, assert_standard_openings
from .functions.aws.aws_lambda import invoke_quality_checker_lambda, re_process_payload
from .functions.aws.cloudwatch import get_logs, negative_log_check
from .functions.aws.dynamodb import get_latest_sequence_id_for_a_given_odscode, get_stored_events_from_dynamo_db
from .functions.aws.s3 import get_s3_email_file
from .functions.aws.sqs import post_to_change_event_dlq, post_ur_fifo, post_ur_sqs
from .functions.context import Context
from .functions.dos.check_data import (
    check_pending_service_is_rejected,
    check_service_history,
    check_service_history_change_type,
    service_history_negative_check,
)
from .functions.dos.get_data import (
    get_blood_pressure_sgsd,
    get_change_event_specified_opening_times,
    get_change_event_standard_opening_times,
    get_contraception_sgsd,
    get_locations_table_data,
    get_palliative_care,
    get_service_history,
    get_service_history_specified_opening_times,
    get_service_history_standard_opening_times,
    get_service_id,
    get_service_table_field,
    get_services_table_location_data,
    wait_for_service_update,
)
from .functions.dos.translation import get_service_table_field_name, get_status_id
from .functions.generator import (
    add_blood_pressure_to_change_event,
    add_contraception_to_change_event,
    add_palliative_care_to_change_event,
    add_single_opening_day,
    add_specified_openings_to_dos,
    add_standard_openings_to_dos,
    apply_blood_pressure_to_service,
    apply_contraception_to_service,
    apply_palliative_care_to_service,
    build_change_event,
    build_change_event_contacts,
    build_change_event_opening_times,
    build_change_event_services,
    commit_new_service_to_dos,
    generate_staff,
    query_specified_opening_builder,
    query_standard_opening_builder,
    remove_palliative_care_to_change_event,
    valid_change_event,
)
from .functions.slack import slack_retry
from .functions.utils import (
    convert_specified_opening,
    convert_standard_opening,
    create_pending_change_for_service,
    generate_correlation_id,
    generate_random_int,
    get_address_string,
    get_expected_data,
    quality_checker_log_check,
    quality_checker_negative_log_check,
)

scenarios(
    "../features/F001_Valid_Change_Events.feature",
    "../features/F002_Invalid_Change_Events.feature",
    "../features/F003_DoS_Security.feature",
    "../features/F004_Error_Handling.feature",
    "../features/F005_Support_Functions.feature",
    "../features/F006_Opening_Times.feature",
    "../features/F007_Reporting.feature",
    "../features/F008_Quality_Checker.feature",
)
FAKER = Faker("en_GB")


@given(parse('the "{contact}" is changed and is valid'), target_fixture="context")
def a_changed_contact_event_is_valid(contact: str, context: Context) -> Context:
    """Change a contact and validate the change event.

    Args:
        contact (str): The contact to change.
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    validated = False
    while not validated:
        match contact.lower():
            case "website":
                context.previous_value = context.change_event["Contacts"][1]["ContactValue"]
                context.website = f"{FAKER.domain_word()}.nhs.uk"
                context.generator_data["web"] = context.website
                context.change_event["Contacts"] = build_change_event_contacts(context)
            case "phone_no":
                context.previous_value = context.change_event["Contacts"][0]["ContactValue"]
                context.phone = FAKER.phone_number()
                context.generator_data["publicphone"] = context.phone
                context.change_event["Contacts"] = build_change_event_contacts(context)
            case "address":
                context.previous_value = get_address_string(context)
                context.change_event["Address1"] = FAKER.street_name()
            case _:
                msg = f"ERROR!.. Input parameter '{contact}' not compatible"
                raise ValueError(msg)
        validated = valid_change_event(context)
    return context


@given("an entry is created in the services table", target_fixture="context")
def a_service_table_entry_is_created(context: Context, ods_code: int = 0, service_type: int = 13) -> Context:
    """Create a new entry in the services table.

    Args:
        context (Context): The context object.
        ods_code (int, optional): The ODS code to use. Defaults to 0.
        service_type (int, optional): The service type to use. Defaults to 13.

    Returns:
        Context: The context object.
    """
    if ods_code == 0:
        ods_code = str(randint(10000, 99999))
    query_values = {
        "uid": f"test{randint(10000, 99999)!s}",
        "service_type": service_type,
        "service_status": 1,
        "name": f"Test Pharmacy {randint(100, 999)!s}",
        "odscode": ods_code,
        "address": f"{randint(100, 999)!s} Test Address",
        "town": "Nottingham",
        "postcode": "NG11GS",
        "publicphone": f"{randint(10000000000, 99999999999)!s}",
        "web": "www.google.com",
        "blood pressure": False,
        "contraception": False,
    }
    context.generator_data = query_values
    return context


@given("the service in DoS supports palliative care", target_fixture="context")
def add_palliative_care_to_dos(context: Context) -> Context:
    """Add a palliative care entry to the service in DoS.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    context.other = apply_palliative_care_to_service(context)
    return context


@given("the change event has a palliative care entry", target_fixture="context")
def _(context: Context) -> Context:
    """Add a palliative care uecservice to the change event.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    add_palliative_care_to_change_event(context)
    return context


@given("the change event has no palliative care entry", target_fixture="context")
def _(context: Context) -> Context:
    """Remove a palliative care uecservice to the change event.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    remove_palliative_care_to_change_event(context)
    return context


@given("the change event has a blood pressure entry", target_fixture="context")
def _(context: Context) -> Context:
    """Add a blood pressure service entry to the change event.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    add_blood_pressure_to_change_event(context)
    return context


@given("the change event has a contraception entry", target_fixture="context")
def _(context: Context) -> Context:
    """Add a contraception service entry to the change event.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    add_contraception_to_change_event(context)
    return context


@given(parse('"{count}" basic services are created'), target_fixture="context")
def create_multiple_basic_service_entry(context: Context, count: str) -> Context:
    """Create multiple basic services.

    Args:
        context (Context): The context object.
        count (str): The number of services to create.

    Returns:
        Context: The context object.
    """
    context = a_service_table_entry_is_created(context)
    context = service_table_entry_is_committed(context)
    ods_code = context.generator_data["odscode"]
    for _ in range(int(count) - 1):
        context = a_service_table_entry_is_created(context, ods_code)
        context = service_table_entry_is_committed(context)
    return context


@given("a basic service is created", target_fixture="context")
def create_basic_service_entry(context: Context) -> Context:
    """Create a basic service.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    context = a_service_table_entry_is_created(context)
    return service_table_entry_is_committed(context)


@given(parse('a pharmacy service is created with type "{service_type:d}"'), target_fixture="context")
def _(context: Context, service_type: int) -> Context:
    """Create a basic service with a specific service type.

    Args:
        context (Context): The context object.
        service_type (int): The service type to use.

    Returns:
        Context: The context object.
    """
    context = a_service_table_entry_is_created(context, service_type=service_type)
    return service_table_entry_is_committed(context)


@given(
    parse('a basic service is created with "{odscode_character_length:d}" character odscode'),
    target_fixture="context",
)
def _(context: Context, odscode_character_length: int) -> Context:
    """Create a basic service with a specific osdcode length.

    Args:
        context (Context): The context object.
        odscode_character_length (int): The length of the odscode to use.
        service_type (int): The service type to use.

    Returns:
        Context: The context object.
    """
    min_value = f"1{'0'* (odscode_character_length-1)} "
    max_value = "9" * odscode_character_length
    odscode = randint(int(min_value), int(max_value))
    context = a_service_table_entry_is_created(context, ods_code=odscode)
    context = service_table_entry_is_committed(context)
    short_odscode = str(odscode)[:5]
    context.ods_code = short_odscode
    context.generator_data["odscode"] = short_odscode
    context.change_event["ODSCode"] = short_odscode
    return context


@given(
    parse(
        'a pharmacy service is created with "{odscode_character_length:d}" character odscode '
        'and type "{service_type:d}"',
    ),
    target_fixture="context",
)
def _(context: Context, odscode_character_length: int, service_type: int) -> Context:
    """Create a basic service with a specific service type and an ods code of a certain length.

    Args:
        context (Context): The context object.
        odscode_character_length (int): The length of the odscode to use.
        service_type (int): The service type to use.

    Returns:
        Context: The context object.
    """
    min_value = f"1{'0'* (odscode_character_length-1)} "
    max_value = "9" * odscode_character_length
    odscode = randint(int(min_value), int(max_value))
    context = a_service_table_entry_is_created(context, ods_code=odscode, service_type=service_type)
    context = service_table_entry_is_committed(context)
    short_odscode = str(odscode)[:5]
    context.ods_code = short_odscode
    context.generator_data["odscode"] = short_odscode
    context.change_event["ODSCode"] = short_odscode
    return context


@given(parse('the service "{field_name}" is set to "{values}"'), target_fixture="context")
def service_values_updated_in_context(field_name: str, values: str, context: Context) -> Context:
    """Update the service values in the context object.

    Args:
        field_name (str): The field name to update.
        values (str): The values to update the field with.
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    context.generator_data[field_name] = values
    return context


@given("an entry is created in the services table with a derivative odscode", target_fixture="context")
def _(context: Context) -> Context:
    odscode = f"{context.generator_data['odscode']}A"
    return a_service_table_entry_is_created(context=context, ods_code=odscode)


@given("an entry is created in the services table with a derivative service", target_fixture="context")
def _(context: Context) -> Context:
    context.generator_data["odscode"] = f"{context.generator_data['odscode']}A"
    context.generator_data["id"] = f"{context.generator_data['id']}1"
    context.generator_data["uid"] = f"{context.generator_data['uid']}1"
    return context


@given(parse('the service is "{service_status}" on "{day}"'), target_fixture="context")
def service_standard_opening_set(service_status: str, day: str, context: Context) -> Context:
    """Set the service standard opening times.

    Args:
        service_status (str): The service status to set.
        day (str): The day to set the service status for.
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    if day.lower() not in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
        msg = "Selected day is not valid"
        raise ValueError(msg)
    query_standard_opening_builder(context, service_status, day)
    return context


@given(parse('the change event is "{service_status}" on "{day}"'), target_fixture="context")
def change_event_standard_opening_set(service_status: str, day: str, context: Context) -> Context:
    """Set the change event standard opening times.

    Args:
        service_status (str): The service status to set.
        day (str): The day to set the service status for.
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    if day.lower() not in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
        msg = "Selected day is not valid"
        raise ValueError(msg)
    query_standard_opening_builder(context, service_status, day)
    context.change_event["OpeningTimes"] = build_change_event_opening_times(context)
    return context


@given(parse('the service is "{service_status}" on date "{date}"'), target_fixture="context")
def service_specified_opening_set(service_status: str, date: str, context: Context) -> Context:
    """Set the service specified opening times.

    Args:
        service_status (str): The service status to set.
        date (str): The date to set the service status for.
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    query_specified_opening_builder(context, service_status, date)
    return context


@given(parse('the change event is "{service_status}" on date "{date}"'), target_fixture="context")
def change_event_specified_opening_set(service_status: str, date: str, context: Context) -> Context:
    """Set the change event specified opening times.

    Args:
        service_status (str): The service status to set.
        date (str): The date to set the service status for.
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    query_specified_opening_builder(context, service_status, date)
    context.change_event["OpeningTimes"] = build_change_event_opening_times(context)
    return context


@given(
    parse(
        'the change event specified opening is "{service_status}" from'
        ' "{open_time}" to "{close_time}" on date "{date}"',
    ),
    target_fixture="context",
)
def change_event_specified_opening_set_times(
    service_status: str,
    date: str,
    open_time: str,
    close_time: str,
    context: Context,
) -> Context:
    """Set the change event specified opening times.

    Args:
        service_status (str): The service status to set.
        date (str): The date to set the service status for.
        open_time (str): The opening time to set.
        close_time (str): The closing time to set.
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    query_specified_opening_builder(context, service_status, date, open_time, close_time)
    context.change_event["OpeningTimes"] = build_change_event_opening_times(context)
    return context


@given("the change event has no standard opening times", target_fixture="context")
def _(context: Context) -> Context:
    """Remove the specified opening dates from the change event.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    context.generator_data["standard_openings"] = []
    context.change_event["OpeningTimes"] = build_change_event_opening_times(context)
    return context


@given("the change event has no specified opening dates", target_fixture="context")
def change_event_no_specified_opening_dates(context: Context) -> Context:
    """Remove the specified opening dates from the change event.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
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
def service_table_entry_is_committed(context: Context) -> Context:
    """Commit the entry to the services table.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    context = commit_new_service_to_dos(context)
    ce_state = False
    if "standard_openings" in context.generator_data:
        add_standard_openings_to_dos(context)
        ce_state = True
    if "specified_openings" in context.generator_data:
        add_specified_openings_to_dos(context)
    if context.change_event is None:
        build_change_event(context)
    if not ce_state:
        add_single_opening_day(context)
    context.change_event["OpeningTimes"] = build_change_event_opening_times(context)
    return context


@given(parse('the change event "{field_name}" is set to "{values}"'), target_fixture="context")
def ce_values_updated_in_context(field_name: str, values: str, context: Context) -> Context:
    """Update the change event values in the context.

    Args:
        field_name (str): The field name to update.
        values (str): The values to update the field with.
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    if field_name.lower() == "website":
        context.previous_value = context.generator_data["web"]
        context.generator_data["web"] = values
        context.change_event["Contacts"] = build_change_event_contacts(context)
    elif field_name.lower() == "phone":
        values = values.replace('"', "")
        context.previous_value = context.generator_data["publicphone"]
        context.generator_data["publicphone"] = values
        context.change_event["Contacts"] = build_change_event_contacts(context)
    elif field_name.lower() == "blood pressure":
        context.generator_data["blood pressure"] = literal_eval(values)
        context.change_event["Services"] = build_change_event_services(context)
    elif field_name.lower() == "contraception":
        context.generator_data["contraception"] = literal_eval(values)
        context.change_event["Services"] = build_change_event_services(context)
    else:
        context.previous_value = context.change_event[field_name]
        context.change_event[field_name] = values
    return context


@given("the change event staff field is populated", target_fixture="context")
def ce_staff_field_populated(context: Context) -> Context:
    """Populate the change event staff field.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    context.change_event["Staff"] = generate_staff()
    return context


@given("the change event has no staff field", target_fixture="context")
def ce_staff_field_removed(context: Context) -> Context:
    """Remove the change event staff field.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    del context.change_event["Staff"]
    return context


@given(parse('the specified opening date is set to "{future_past}" date'), target_fixture="context")
def future_set_specified_opening_date(future_past: str, context: Context) -> Context:
    """Set the specified opening date to a future or past date.

    Args:
        future_past (str): The future or past date to set.
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    year = 0
    if future_past.lower() == "future":
        year = dt.now(tz=timezone("Europe/London")).year + 1
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
            },
        )
    else:
        for days in context.change_event["OpeningTimes"]:
            if days["OpeningTimeType"] == "Additional":
                context.change_event["OpeningTimes"].remove(days)
    return context


@given("a pending entry exists in the changes table for this service", target_fixture="context")
def change_table_entry_creation_for_service(context: Context) -> Context:
    """Create a pending entry in the changes table for the service.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    service_id = context.generator_data["id"]
    service_uid = context.generator_data["uid"]
    context.service_uid = service_uid
    create_pending_change_for_service(service_id)
    return context


@given(parse('the "{contact}" value has been unset'), target_fixture="context")
def changed_event_contact_removed(contact: str, context: Context) -> Context:
    """Remove the contact from the change event.

    Args:
        contact (str): The contact to remove.
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
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
            msg = f"Invalid contact '{contact}' provided"
            raise ValueError(msg)
    return context


@given(parse('the Changed Event has "{amount}" break in opening times'), target_fixture="context")
def change_event_with_break_in_opening_times(context: Context, amount: str) -> Context:
    """Create a change event with a break in the opening times.

    Args:
        context (Context): The context object.
        amount (str): The amount of breaks to add.

    Returns:
        Context: The context object.
    """
    context.generator_data["standard_openings"] = []
    if amount in {"1", "2", "3"}:
        query_standard_opening_builder(context, "open", "monday", "09:00", "12:00")
        query_standard_opening_builder(context, "open", "monday", "12:30", "16:00")
    if amount in {"2", "3"}:
        query_standard_opening_builder(context, "open", "monday", "16:10", "16:30")
    if amount in {"3"}:
        query_standard_opening_builder(context, "open", "monday", "16:40", "17:00")
    context.change_event["OpeningTimes"] = build_change_event_opening_times(context)
    return context


# Weekday NOT present on the Opening Time
@given("the change event has no weekday present in opening times", target_fixture="context")
def a_change_event_with_no_openingtimes_weekday(context: Context) -> Context:
    """Remove the weekday from the change event opening times.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    del context.change_event["OpeningTimes"][0]["Weekday"]
    return context


# OpeningTimeType is NOT "General" or "Additional"
@given("the change event has an invalid openingtimetype", target_fixture="context")
def a_change_event_with_invalid_openingtimetype(context: Context) -> Context:
    """Set the opening time type to an invalid value.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    context.change_event["OpeningTimes"][0]["OpeningTimeType"] = "F8k3"
    return context


# IsOpen is true AND Times is blank
@given("the change event has undefined opening and closing times", target_fixture="context")
def no_times_data_within_openingtimes(context: Context) -> Context:
    """Remove the opening and closing times from the change event.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    context.change_event["OpeningTimes"][0]["OpeningTime"] = ""
    context.change_event["OpeningTimes"][0]["ClosingTime"] = ""
    return context


# isOpen is false AND Times in NOT blank
@given("the change event has opening times open status set to false", target_fixture="context")
def a_change_event_with_isopen_status_set_to_false(context: Context) -> Context:
    """Set the opening times open status to false.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    context.change_event["OpeningTimes"][0]["IsOpen"] = False
    return context


# OpeningTimeType is Additional AND AdditionalOpening Date is Blank
@given("the change event has an additional date with no specified date", target_fixture="context")
def specified_opening_date_not_defined(context: Context) -> Context:
    """Remove the additional opening date from the change event.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
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
        },
    )
    return context


@given(parse('the correlation-id is "{custom_correlation}"'), target_fixture="context")
def a_custom_correlation_id_is_set(context: Context, custom_correlation: str) -> Context:
    """Set the correlation id to a custom value.

    Args:
        context (Context): The context object.
        custom_correlation (str): The custom correlation id.

    Returns:
        Context: The context object.
    """
    context.correlation_id = generate_correlation_id(custom_correlation)
    return context


@given("the ODS has an entry in dynamodb", target_fixture="context")
def create_ods_in_ddb(context: Context) -> Context:
    """Create an ODS entry in dynamodb.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    context = the_change_event_is_sent_with_custom_sequence(context, 100)
    context.sequence_number = 100
    context.unique_key = generate_random_int()
    return context


@given("the Changed Event has blank opening times", target_fixture="context")
def change_event_with_blank_opening_times(context: Context) -> Context:
    """Create a change event with blank opening times.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    context.change_event["OpeningTimes"] = []
    return context


@when(parse('a "{queue_type}" SQS message is added to the queue'), target_fixture="context")
def post_an_sqs_message(queue_type: str, context: Context) -> None:
    """Post an SQS message to the queue.

    Args:
        queue_type (str): The type of queue to post to.
        context (Context): The context object.
    """
    match queue_type.lower():
        case "change event dlq":
            post_to_change_event_dlq(context)
        case "update request dlq":
            post_ur_sqs()
        case "update request failure":
            post_ur_fifo()
        case _:
            msg = f"ERROR!.. queue type '{queue_type}' is not valid"
            raise ValueError(msg)


@when(parse('the Changed Event is sent for processing with "{valid_or_invalid}" api key'), target_fixture="context")
def the_change_event_is_sent_for_processing(context: Context, valid_or_invalid: str) -> Context:
    """Send the change event for processing.

    Args:
        context (Context): The context object.
        valid_or_invalid (str): The type of api key to use.

    Returns:
        Context: The context object.
    """
    if context.phone is not None or context.website is not None:
        context.change_event["Contacts"] = build_change_event_contacts(context)
    context.start_time = dt.now(tz=timezone("Europe/London")).timestamp()
    context.correlation_id = generate_correlation_id()
    context.response = process_payload(context, valid_or_invalid == "valid", context.correlation_id)
    context.sequence_number = context.response.request.headers["sequence-number"]
    return context


# Request with custom sequence id
@when(
    parse('the Changed Event is sent for processing with sequence id "{seqid}"'),
    target_fixture="context",
)
def the_change_event_is_sent_with_custom_sequence(context: Context, seqid: str) -> Context:
    """Send the change event for processing with a custom sequence id.

    Args:
        context (Context): The context object.
        seqid (str): The custom sequence id.

    Returns:
        Context: The context object.
    """
    context.start_time = dt.now(tz=timezone("Europe/London")).timestamp()
    context.correlation_id = generate_correlation_id()
    context.response = process_payload_with_sequence(context, context.correlation_id, seqid)
    context.sequence_number = seqid
    context.change_event["Address1"] = context.change_event["Address1"] + " - Updated"
    return context


# Request with no sequence id
@when(
    parse("the Changed Event is sent for processing with no sequence id"),
    target_fixture="context",
)
def the_change_event_is_sent_with_no_sequence(context: Context) -> Context:
    """Send the change event for processing with no sequence id.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    context.start_time = dt.now(tz=timezone("Europe/London")).timestamp()
    context.correlation_id = generate_correlation_id()
    context.response = process_payload_with_sequence(context, context.correlation_id, None)
    return context


# Request with duplicate sequence id
@when(
    parse("the Changed Event is sent for processing with a duplicate sequence id"),
    target_fixture="context",
)
def the_change_event_is_sent_with_duplicate_sequence(context: Context) -> Context:
    """Send the change event for processing with a duplicate sequence id.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    context.start_time = dt.now(tz=timezone("Europe/London")).timestamp()
    context.correlation_id = generate_correlation_id()
    context.change_event["Address1"] = "New Test Address Value"
    seqid = 0
    seqid = 100 if context.sequence_number == 100 else get_latest_sequence_id_for_a_given_odscode(context.ods_code)
    context.response = process_payload_with_sequence(context, context.correlation_id, seqid)
    context.sequence_number = seqid
    return context


@then("the Changed Event is stored in dynamo db")
def stored_dynamo_db_events_are_pulled(context: Context) -> Context:
    """Pull the stored dynamo db events.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
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
def field_is_not_updated_in_dos(context: Context, plain_english_service_table_field: str) -> None:
    """Assert DoS demographics data is not updated.

    Args:
        context (Context): The context object.
        plain_english_service_table_field (str): The plain english service table field.
    """
    sleep(60)
    field_name = get_service_table_field_name(plain_english_service_table_field)
    field_data = get_service_table_field(service_id=context.service_id, field_name=field_name)
    assert (
        context.previous_value in field_data
    ), f"ERROR!.. DoS doesn't have expected {plain_english_service_table_field} data - It has changed from expected value, expected: {context.previous_value}, actual: {field_data}"  # noqa: E501


@then(parse('DoS has "{expected_data}" in the "{plain_english_service_table_field}" field'))
def expected_data_is_within_dos(context: Context, expected_data: str, plain_english_service_table_field: str) -> None:
    """Assert DoS demographics data is updated.

    Args:
        context (Context): The context object.
        expected_data (str): The expected data.
        plain_english_service_table_field (str): The plain english service table field.
    """
    wait_for_service_update(context.service_id)
    field_name = get_service_table_field_name(plain_english_service_table_field)
    field_data = get_service_table_field(service_id=context.service_id, field_name=field_name)
    if plain_english_service_table_field in {"easting", "northing", "status"}:
        expected_data = int(expected_data)
    elif plain_english_service_table_field in {"latitude", "longitude"}:
        expected_data = float(expected_data)
    elif plain_english_service_table_field in {"phone"}:
        expected_data = expected_data.replace(" ", "")
    assert (
        field_data == expected_data
    ), f"ERROR!.. DoS doesn't have expected {plain_english_service_table_field} data, expected: {expected_data}, actual: {field_data}"  # noqa: E501


@then(parse('the "{plain_english_service_table_field}" is updated within the DoS DB'))
def check_the_service_table_field_has_updated(context: Context, plain_english_service_table_field: str) -> Context:
    """Assert DoS demographics data is updated.

    Args:
        context (Context): The context object.
        plain_english_service_table_field (str): The plain english service table field.

    Returns:
        Context: The context object.
    """
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
def check_the_service_history_has_updated(context: Context, plain_english_service_table_field: str) -> Context:
    """Assert DoS demographics data is updated.

    Args:
        context (Context): The context object.
        plain_english_service_table_field (str): The plain english service table field.

    Returns:
        Context: The context object.
    """
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
def check_service_history_specified_times(context: Context, added_or_removed: str) -> Context:
    """Assert DoS specified opening times data is updated.

    Args:
        context (Context): The context object.
        added_or_removed (str): The added or removed.

    Returns:
        Context: The context object.
    """
    match added_or_removed:
        case "added":
            change_type = "add"
        case "removed":
            change_type = "remove"
        case "closed":
            change_type = "add"
        case _:
            msg = "Invalid change type has been provided"
            raise ValueError(msg)
    if change_type == "add":
        openingtimes = context.change_event["OpeningTimes"][-1]
    elif change_type == "remove":
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
def check_service_history_standard_times(context: Context, added_or_removed: str) -> Context:
    """Assert DoS standard opening times data is updated.

    Args:
        context (Context): The context object.
        added_or_removed (str): The added or removed.

    Returns:
        Context: The context object.
    """
    sleep(10)
    openingtimes = context.change_event["OpeningTimes"]
    dos_times = get_service_history_standard_opening_times(context.service_id)
    expected_dates = convert_standard_opening(openingtimes)
    counter = 0
    strict_checks = "f006s012" in environ.get("PYTEST_CURRENT_TEST")
    if added_or_removed == "added":
        counter = assert_standard_openings("add", dos_times, expected_dates, strict_checks)
    elif added_or_removed == "modified":
        counter = assert_standard_openings("modify", dos_times, expected_dates, strict_checks)
    else:
        counter = assert_standard_closing(dos_times, expected_dates)
    if counter == 0:
        msg = "ERROR: No Assertions have been made"
        raise ValueError(msg)
    return context


@then(parse("the service history is not updated"))
def check_service_history_not_updated(context: Context) -> Context:
    """Assert DoS service history is not updated.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    service_history_status = service_history_negative_check(context.service_id)
    assert service_history_status == "Not Updated", "ERROR: Service history was unexpectedly updated"
    # will revisit to change the assertion type to boolean rather string
    return context


@then(parse('the service history shows change type is "{change_type}"'))
def check_service_history_for_change_type(context: Context, change_type: str) -> Context:
    """Assert DoS service history change type is updated.

    Args:
        context (Context): The context object.
        change_type (str): The change type.

    Returns:
        Context: The context object.
    """
    # This brings instability if more than one entry has been changed
    change_status = check_service_history_change_type(context.service_id, change_type)
    assert change_status == "Change type matches", f"ERROR: Expected {change_type} but {change_status}"
    return context


@then(parse('the service history shows "{field_name}" change type is "{change_type}"'))
def check_service_history_for_specific_change_type(context: Context, change_type: str, field_name: str) -> Context:
    """Assert DoS service history change type is updated.

    Args:
        context (Context): The context object.
        change_type (str): The change type.
        field_name (str): The field name.

    Returns:
        Context: The context object.
    """
    change_status = check_service_history_change_type(context.service_id, change_type, field_name)
    assert change_status == "Change type matches", f"ERROR: Expected {change_type} but {change_status}"
    return context


@then("the DoS service has been updated with the specified date and time is captured by DoS")
def the_dos_service_has_been_updated_with_the_specified_date_and_time_is_captured_by_dos(context: Context) -> Context:
    """Assert DoS service has been updated with the specified date and time is captured by DoS.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
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
def the_dos_service_has_no_past_openings(context: Context, year: str) -> None:
    """Assert DoS service has no past openings.

    Args:
        context (Context): The context object.
        year (str): The year.
    """
    wait_for_service_update(context.generator_data["id"])
    current_specified_openings = get_change_event_specified_opening_times(context.generator_data["id"])
    if current_specified_openings != {}:
        assert year not in current_specified_openings, f"{year} not found in {current_specified_openings}"


@then("the DoS service has been updated with the standard days and times is captured by DoS")
def the_dos_service_has_been_updated_with_the_standard_days_and_times_is_captured_by_dos(context: Context) -> None:
    """Assert DoS service has been updated with the standard days and times is captured by DoS.

    Args:
        context (Context): The context object.
    """
    context.service_id = get_service_id(context.change_event["ODSCode"])
    wait_for_service_update(context.service_id)
    open_time = context.change_event["OpeningTimes"][0]["OpeningTime"]
    closing_time = context.change_event["OpeningTimes"][0]["ClosingTime"]
    current_standard_openings = get_change_event_standard_opening_times(context.service_id)
    assert "Monday" in current_standard_openings, "DoS not updated with standard opening time"
    assert current_standard_openings["Monday"][0]["start_time"] == open_time
    assert current_standard_openings["Monday"][0]["end_time"] == closing_time


@then(parse('the change event response has status code "{status}"'))
def step_then_should_transform_into(context: Context, status: str) -> None:
    """Assert the change event response has status code.

    Args:
        context (Context): The context object.
        status (str): The status code.
    """
    message = context.response.json
    assert (
        str(context.response.status_code) == status
    ), f"Status code not as expected: {context.response.status_code} != {status} Error: {message} - {status}"


@then("the response has security headers")
def step_then_security_headers_are_present(context: Context) -> None:
    """Assert the change event response has security headers.

    Args:
        context (Context): The context object.
    """
    expected_headers = {
        "X-Frame-Options": "DENY",
        "Content-Security-Policy": "default-src 'self'",
        "X-Content-Type-Options": "nosniff",
    }

    for header, expected_value in expected_headers.items():
        assert header in context.response.headers, f"'{header}' header is missing in the response"
        assert (
            context.response.headers[header] == expected_value
        ), f"'{header}' value is not as expected: {context.response.headers[header]} != {expected_value}"


@then(parse('"{attribute}" attribute is identified in the "{report}" report in "{lambda_name}" logs'))
def step_then_attribute_is_identified_in_the_report(
    context: Context,
    attribute: str,
    report: str,
    lambda_name: str,
) -> None:
    """Assert the attribute is identified in the report in lambda logs.

    Args:
        context (Context): The context object.
        attribute (str): Attribute name.
        report (str): Report name.
        lambda_name (str): Lambda name.
    """
    query = (
        f'fields @message | sort @timestamp asc | filter correlation_id="{context.correlation_id}"'
        f'| filter report_key="{report}"'
    )
    logs = get_logs(query, lambda_name, context.start_time)
    assert attribute in logs


@then("the stored Changed Event is reprocessed in DI")
def replaying_changed_event(context: Context) -> Context:
    """Assert the stored Changed Event is reprocessed in DI.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    response = re_process_payload(context.change_event["ODSCode"], context.sequence_number)
    assert (
        "The change event has been re-sent successfully" in response
    ), f"Error!.. Failed to re-process Change event. Message: {response}"
    context.correlation_id = ast.literal_eval(loads(response)).get("correlation_id")
    return context


@then("opening times with a break are updated in DoS")
def opening_times_with_a_break_are_updated_in_dos(context: Context) -> None:
    """Assert opening times with a break are updated in DoS.

    Args:
        context (Context): The context object.
    """
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
def opening_times_with_two_breaks_are_updated_in_dos(context: Context) -> None:
    """Assert opening times with two breaks are updated in DoS.

    Args:
        context (Context): The context object.
    """
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
def the_changed_opening_time_is_accepted_by_dos(context: Context, date: str) -> Context:
    """Assert the changed opening time is accepted by DoS.

    Args:
        context (Context): The context object.
        date (str): The date.

    Returns:
        Context: The context object.
    """
    wait_for_service_update(context.generator_data["id"])
    current_specified_openings = get_change_event_specified_opening_times(context.generator_data["id"])
    expected_opening_date = dt.strptime(date, "%b %d %Y").strftime("%Y-%m-%d")
    assert expected_opening_date in current_specified_openings, "DoS not updated with specified opening time"
    assert current_specified_openings[expected_opening_date] != [], "Date is not open in DoS"
    return context


@then(parse('DoS is open from "{open_time}" until "{close_time}" on "{date}"'), target_fixture="context")
def the_changed_opening_time_is_accepted_by_dos_specific(
    context: Context,
    date: str,
    open_time: str,
    close_time: str,
) -> Context:
    """Assert the changed opening time is accepted by DoS.

    Args:
        context (Context): The context object.
        date (str): The date.
        open_time (str): The open time.
        close_time (str): The close time.

    Returns:
        Context: The context object.
    """
    wait_for_service_update(context.generator_data["id"])
    current_specified_openings = get_change_event_specified_opening_times(context.generator_data["id"])
    expected_opening_date = dt.strptime(date, "%b %d %Y").strftime("%Y-%m-%d")
    assert expected_opening_date in current_specified_openings, "DoS not updated with specified opening time"
    assert (
        current_specified_openings[expected_opening_date][0]["start_time"] == open_time
    ), "Date is not open at correct times"
    assert (
        current_specified_openings[expected_opening_date][0]["end_time"] == close_time
    ), "Date is not closed at correct times"
    return context


@then(parse('DoS is closed on "{date}"'), target_fixture="context")
def the_changed_closing_time_is_accepted_by_dos(context: Context, date: str) -> Context:
    """Assert the changed closing time is accepted by DoS.

    Args:
        context (Context): The context object.
        date (str): The date.

    Returns:
        Context: The context object.
    """
    wait_for_service_update(context.generator_data["id"])
    current_specified_openings = get_change_event_specified_opening_times(context.generator_data["id"])
    expected_opening_date = dt.strptime(date, "%b %d %Y").strftime("%Y-%m-%d")
    assert expected_opening_date in current_specified_openings, "DoS not updated with specified opening time"
    assert current_specified_openings[expected_opening_date] == [], "Date is not closed in DoS"
    return context


@then(parse('there is no longer a specified opening on "{date}"'), target_fixture="context")
def specified_date_is_removed_from_dos(context: Context, date: str) -> Context:
    """Assert specified date is removed from DoS.

    Args:
        context (Context): The context object.
        date (str): The date.

    Returns:
        Context: The context object.
    """
    sleep(60)
    current_specified_openings = get_change_event_specified_opening_times(context.generator_data["id"])
    expected_opening_date = dt.strptime(date, "%b %d %Y").strftime("%Y-%m-%d")
    assert (
        expected_opening_date not in current_specified_openings
    ), f"Specified date {expected_opening_date} not removed from DoS"
    return context


@then(parse('the pharmacy is confirmed "{open_or_closed}" on "{day}"'), target_fixture="context")
def standard_day_confirmed_open_check(context: Context, open_or_closed: str, day: str) -> Context:
    """Assert the pharmacy is confirmed open or closed on a standard day.

    Args:
        context (Context): The context object.
        open_or_closed (str): The open or closed status.
        day (str): The day.

    Returns:
        Context: The context object.
    """
    context.service_id = context.generator_data["id"]
    sleep(60)
    opening_time_event = get_change_event_standard_opening_times(context.service_id)
    match open_or_closed.upper():
        case "CLOSED":
            assert opening_time_event[day] == [], f'ERROR!.. Pharmacy is CLOSED but expected to be OPEN for "{day}"'
        case "OPEN":
            assert opening_time_event[day] != [], f'ERROR!.. Pharmacy is OPEN but expected to be CLOSED for "{day}"'
        case _:
            msg = f'Invalid status input parameter: "{open_or_closed}"'
            raise ValueError(msg)
    return context


@then(parse('the "{lambda_name}" lambda shows field "{field}" with value "{message}"'))
def generic_lambda_log_check_function(context: Context, lambda_name: str, field: str, message: str) -> None:
    """Assert the lambda log contains the expected message.

    Args:
        context (Context): The context object.
        lambda_name (str): The lambda name.
        field (str): The field.
        message (str): The message.
    """
    if "/" in context.correlation_id:
        context.correlation_id = context.correlation_id.replace("/", r"\/")
    query = (
        f"fields {field} | sort @timestamp asc"
        f' | filter correlation_id="{context.correlation_id}" | filter {field} like "{message}"'
    )
    logs = get_logs(query, lambda_name, context.start_time)
    assert message in logs, f"ERROR!!.. error event processor did not detect the {field}: {message}."


@then(parse('the "{lambda_name}" lambda shows "{count}" of "{field}" with value "{message}"'))
def generic_lambda_multiple_log_check_function(
    context: Context,
    lambda_name: str,
    count: str,
    field: str,
    message: str,
) -> None:
    """Assert the lambda log contains the expected message.

    Args:
        context (Context): The context object.
        lambda_name (str): The lambda name.
        count (str): The count.
        field (str): The field.
        message (str): The message.
    """
    if "/" in context.correlation_id:
        context.correlation_id = context.correlation_id.replace("/", r"\/")
    query = (
        f"fields {field} | sort @timestamp asc"
        f' | filter correlation_id="{context.correlation_id}" | filter {field} like "{message}"'
    )
    logs = get_logs(query, lambda_name, context.start_time)
    assert message in logs, f"ERROR!!.. error event processor did not detect the {field}: {message}."
    assert len(loads(logs)["results"]) == int(count), "ERROR!!.. Incorrect number of log entries"


@then(parse('the "{lambda_name}" lambda does not show "{field}" with value "{message}"'))
def generic_lambda_log_negative_check_function(context: Context, lambda_name: str, field: str, message: str) -> None:
    """Assert the lambda log does not contain the expected message.

    Args:
        context (Context): The context object.
        lambda_name (str): The lambda name.
        field (str): The field.
        message (str): The message.
    """
    find_request_id_query = (
        f'fields function_request_id | sort @timestamp asc | filter correlation_id="{context.correlation_id}"'
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
def slack_message_check(message: str, environment_type: str) -> None:
    """Assert the slack channel contains the expected message.

    Args:
        message (str): The message.
        environment_type (str): The environment type.
    """
    slack_entries = slack_retry(message)
    current_environment = getenv(environment_type)
    assert_string = f"{current_environment} | {message}"
    assert assert_string in slack_entries


@then("the service table has been updated with locations data")
def services_location_update_assertion(context: Context) -> None:
    """Assert the service table has been updated with locations data.

    Args:
        context (Context): The context object.
    """
    sleep(20)
    location_data = get_locations_table_data(context.change_event["Postcode"])
    services_data = get_services_table_location_data(context.service_id)
    assert services_data == location_data, "ERROR: Services and Location data does not match"


@then("the service history table has been updated with locations data")
def services_location_history_update_assertion(context: Context) -> None:
    """Assert the service history table has been updated with locations data.

    Args:
        context (Context): The context object.
    """
    sleep(10)
    history_data = get_service_history(context.service_id)
    history_data = history_data[next(iter(history_data.keys()))]["new"]
    history_list = [
        history_data["cmsorgtown"]["data"],
        history_data["postalcode"]["data"],
        history_data["cmseastings"]["data"],
        history_data["cmsnorthings"]["data"],
    ]
    location_data = get_locations_table_data(context.change_event["Postcode"])
    location_data = list(location_data[0].values())[:-2]
    assert history_list == location_data, "ERROR: Service History and Location data does not match"


@then("the s3 bucket contains an email file matching the service uid")
def check_s3_contains_email_file(context: Context) -> None:
    """Assert the s3 bucket contains an email file matching the service uid.

    Args:
        context (Context): The context object.
    """
    get_s3_email_file(context)
    assert context.service_uid in context.other["email_body"], "ERROR: service_uid not found in email body"


@then("the changes table shows change is now rejected")
def check_changes_table_has_been_updated(context: Context) -> None:
    """Assert the changes table shows change is now rejected.

    Args:
        context (Context): The context object.
    """
    status = check_pending_service_is_rejected(context.service_id)
    assert "REJECTED" in status, "ERROR: changes table has not been updated"


@then("service sync log contains no overlapping log data", target_fixture="context")
def show_service_sync_logs(context: Context) -> None:
    """Assert the service sync log contains no overlapping log data.

    Args:
        context (Context): The context object.
    """
    query = (
        f'fields @message | sort @timestamp asc | filter correlation_id="{context.correlation_id}"'
        '|filter message like "Attempting connection to database"'
    )
    logs = loads(get_logs(query, "service-sync", context.start_time))["results"][0][0]["value"]
    assert "service_name" not in logs, "ERROR: service name found in logs"
    assert "service_uid" not in logs, "ERROR: service uid found in logs"


@then("logs show staff data has been redacted", target_fixture="context")
def ingest_staff_redaction(context: Context) -> Context:
    """Assert the logs show staff data has been redacted.

    Args:
        context (Context): The context object.
    """
    query = 'fields @message | sort @timestamp asc | filter message like "key from Change Event payload"'
    logs = loads(get_logs(query, "ingest-change-event", context.start_time))
    assert logs != [], "ERROR: Logs do not show redaction of staff field"
    return context


@then("error messages do not show Staff data", target_fixture="context")
def error_contains_no_staff(context: Context) -> Context:
    """Assert the error messages do not show Staff data.

    Args:
        context (Context): The context object.
    """
    query = (
        f'fields @event | sort @timestamp asc | filter correlation_id="{context.correlation_id}"'
        '|filter message like "Validation Error - Unexpected Org Sub Type ID"'
    )
    logs = loads(get_logs(query, "ingest-change-event", context.start_time))
    assert "Superintendent Pharmacist" not in logs, "ERROR: Logs output the staff field on error"
    return context


@then(parse('palliative care is "{action}" to the service'), target_fixture="context")
def _(context: Context, action: str) -> Context:
    """Assert palliative care is applied to the service.

    Args:
        context (Context): The context object.
        action (str): The action.

    Returns:
        Context: The context object.
    """
    match action:
        case "added":
            applied = True
            palliative_care = get_palliative_care(context.service_id)
        case "removed":
            applied = False
            palliative_care = get_palliative_care(context.service_id)
        case "applied":
            applied = True
            palliative_care = get_palliative_care(context.service_id, wait_for_update=False)
        case "not applied":
            applied = False
            palliative_care = get_palliative_care(context.service_id, wait_for_update=False)
        case _:
            msg = f"Unexpected action: {action}"
            raise ValueError(msg)

    assert palliative_care == applied, "ERROR: Palliative care not correctly applied/removed to DoS service"
    return context


@then(parse("blood pressure Z Code is added to the service"), target_fixture="context")
def _(context: Context) -> Context:
    """Assert the error messages do not show Staff data.

    Args:
        context (Context): The context object.
        action (str): The action.

    Returns:
        Context: The context object.
    """
    blood_pressure = get_blood_pressure_sgsd(context.service_id)
    assert blood_pressure is True, "ERROR Blood Pressure not correctly applied to DoS service"
    return context


@then(parse("contraception Z Code is added to the service"), target_fixture="context")
def _(context: Context) -> Context:
    """Assert the error messages do not show Staff data.

    Args:
        context (Context): The context object.
        action (str): The action.

    Returns:
        Context: The context object.
    """
    contraception = get_contraception_sgsd(context.service_id)
    assert contraception is True, "ERROR Contraception not correctly applied to DoS service"
    return context


@then(
    parse("Hidden or Closed logs does not show closed services or not going to active services"),
    target_fixture="context",
)
def _(context: Context) -> Context:
    logs = get_logs(
        query=f"fields @message | filter report_key == 'HIDDEN_OR_CLOSED' | filter correlation_id == '{context.correlation_id}' | sort @timestamp",  # noqa: E501
        lambda_name="service-matcher",
        start_time=context.start_time,
    )
    results = loads(logs)["results"]
    value = loads(results[0][0]["value"])
    count = [result["value"] for result in results[0] if result["field"] == "@message"]
    assert value["dos_service_typeid"] == 13, "ERROR: Incorrect service type id found"
    assert len(count) == 1, "ERROR: More than one log entry found"
    return context


@given(
    parse(
        "{service_count:d} {service_status} services of type {service_type:d} for an odscode starting with {starting_character}",  # noqa: E501
    ),
    target_fixture="context",
)
def _(context: Context, service_count: int, service_status: str, service_type: int, starting_character: str) -> Context:
    """Create number of services of a given type and status for an odscode starting with a specific starting character.

    Args:
        context (Context): The context object.
        service_count (int): The number of services.
        service_status (str): The service status.
        service_type (int): The service type.
        starting_character (str): The starting character.

    Returns:
        Context: The context object.
    """
    odscode = f"{starting_character.upper()}{randint(1000, 9999)}"
    context.ods_code = odscode
    for _ in range(service_count):
        context = a_service_table_entry_is_created(context, odscode)
        context.generator_data["service_status"] = get_status_id(service_status)
        context.generator_data["service_type"] = service_type
        context = service_table_entry_is_committed(context)
    return context


@given(
    parse(
        "an active service of type {service_type:d} for a {character_count:d} character odscode starting with {starting_character}",  # noqa: E501
    ),
    target_fixture="context",
)
def _(context: Context, service_type: int, character_count: int, starting_character: str) -> Context:
    """Create an active service of given type for a defined length odscode starting with a specific starting character.

    Args:
        context (Context): The context object.
        service_type (int): The service type.
        character_count (int): The character count.
        starting_character (str): The starting character.

    Returns:
        Context: The context object.
    """
    min_value = f"{'0'* (character_count-2)} "
    max_value = "9" * (character_count - 1)
    odscode = f"{starting_character}{randint(int(min_value), int(max_value))}"
    context.ods_code = odscode
    context = a_service_table_entry_is_created(context, odscode)
    context.generator_data["service_type"] = service_type
    return service_table_entry_is_committed(context)


@given(parse("the DoS service has {commissioned_service} Z code"), target_fixture="context")
def _(context: Context, commissioned_service: str) -> Context:
    match commissioned_service.lower():
        case "blood pressure":
            apply_blood_pressure_to_service(context)
        case "contraception":
            apply_contraception_to_service(context)
        case "palliative care":
            apply_palliative_care_to_service(context)
        case _:
            msg = f"Unexpected commissioned service: {commissioned_service}"
            raise ValueError(msg)
    return context


@when("the quality checker is run", target_fixture="context")
def _(context: Context) -> Context:
    """Run the quality checker.

    Args:
        context (Context): The context object.

    Returns:
        Context: The context object.
    """
    context.start_time = dt.now(tz=timezone("Europe/London")).timestamp()
    context.response = invoke_quality_checker_lambda()
    return context


@then(parse("the following {reason} is reported {reason_count:d} times"), target_fixture="context")
def _(context: Context, reason: str, reason_count: int) -> Context:
    """Assert the quality checker reports the expected reason.

    Args:
        context (Context): The context object.
        reason (str): The reason in the report.
        reason_count (int): The number of times the reason is reported.

    Returns:
        Context: The context object.
    """
    logs = quality_checker_log_check(
        request_id=context.response["ResponseMetadata"]["RequestId"],
        odscode=context.ods_code or context.generator_data["odscode"],
        reason=reason,
        start_time=context.start_time,
    )
    logs = [log[0]["value"] for log in logs if log[0]["field"] == "message"]
    assert len(logs) == reason_count, f"ERROR: Expected {reason_count} {reason} logs, found {len(logs)}"
    return context


@then(parse("the following {reason} is reported {reason_count:d} times with a long odscode"), target_fixture="context")
def _(context: Context, reason: str, reason_count: int) -> Context:
    """Assert the quality checker reports the expected reason.

    Args:
        context (Context): The context object.
        reason (str): The reason in the report.
        reason_count (int): The number of times the reason is reported.

    Returns:
        Context: The context object.
    """
    logs = quality_checker_log_check(
        request_id=context.response["ResponseMetadata"]["RequestId"],
        odscode=context.ods_code or context.generator_data["odscode"],
        reason=reason,
        start_time=context.start_time,
        match_on_more_than_5_character_odscode=True,
    )
    logs = [log[0]["value"] for log in logs if log[0]["field"] == "message"]
    assert len(logs) == reason_count, f"ERROR: Expected {reason_count} {reason} logs, found {len(logs)}"
    return context


@then(parse("the following {reason} is not reported"), target_fixture="context")
def _(context: Context, reason: str) -> Context:
    """Assert the quality checker reports the expected reason.

    Args:
        context (Context): The context object.
        reason (str): The reason in the report.

    Returns:
        Context: The context object.
    """
    assert (
        quality_checker_negative_log_check(
            request_id=context.response["ResponseMetadata"]["RequestId"],
            odscode=context.ods_code or context.generator_data["odscode"],
            reason=reason,
            start_time=context.start_time,
        )
        is True
    ), f"ERROR: {reason} logs found"
    return context
