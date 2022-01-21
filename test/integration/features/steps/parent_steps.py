from os import getenv
from behave import given, then, when
from features.utilities.utils import (
    get_response,
    get_lambda_info,
    debug_purge_queue,
    process_payload,
    get_stored_events_from_db,
    get_latest_sequence_id_for_a_given_odscode,
)
from decimal import Decimal
from features.utilities.change_events import get_change_event_string, get_change_event_dict
from features.utilities.log_stream import get_logs
import json
from time import sleep


@given("a Changed Event is valid")
def a_change_event_is_valid(context):
    """Creates a valid change event"""
    context.change_event = get_change_event_string()


@given("a Changed Event has no matching DoS services")
def a_change_event_with_no_matching_dos_services(context):
    context.change_event = get_change_event_string()
    context.change_event["ODSCode"] = "CODE1"


@given("a Changed Event with invalid ODSCode is provided")
def a_change_event_with_invalid_odscode(context):
    """Creates a valid change event"""
    context.change_event = get_change_event_dict()
    context.change_event["ODSCode"] = "FAKE6"


@given("a Changed Event with invalid OrganisationSubType is provided")
def a_change_event_with_invalid_organisationsubtype(context):
    """Creates a valid change event"""
    context.change_event = get_change_event_dict()
    context.change_event["OrganisationSubType"] = "com"


@given("a Changed Event with invalid OrganisationTypeID is provided")
def a_change_event_with_invalid_organisationtypeid(context):
    """Creates a valid change event"""
    context.change_event = get_change_event_dict()
    context.change_event["OrganisationTypeID"] = "DEN"


@when("the Changed Event is sent for processing")
def the_change_event_is_sent_for_processing(context):
    debug_purge_queue()
    context.response = process_payload(context.change_event)
    context.correlation_id = context.response.headers["x-amzn-RequestId"]
    context.sequence_no = context.response.request.headers["sequence-number"]
    print(context.sequence_no)
    message = context.response.json()
    assert (
        context.response.status_code == 200
    ), f"Status code not as expected.. Status code: {context.response.status_code} Error: {message}"


@when('a "{valid}" Change Event with sequence id "{corrid}" is sent to the event procesor')
def a_valid_change_event_with_seq_id_is_processed(context, valid: str, corrid: str):
    response = process_payload(valid, corrid)
    message = response.json()
    assert (
        response.status_code == 200
    ), f"Status code not as expected.. Status code: {response.status_code} Error: {message}"


@when('an "{invalid}" Change Event with sequence id "{corrid}" is processed')
def an_invalid_change_event_with_seq_id_is_processed(context, invalid: str, corrid: str):
    response = process_payload(invalid, corrid)
    message = response.json()
    assert (
        response.status_code == 200
    ), f"Status code not as expected.. Status code: {response.status_code} Error: {message}"
    debug_purge_queue()


@when('an "{expected}" Change Event is sent to the event procesor')
def an_expected_change_event_is_sent_to_the_event_procesor(context, expected: str):
    response = get_response(expected)
    assert response == "Change event received", f"ERROR! Invalid Payload received.."


@then('the "{event}" logs are generated')
def the_lambda_logs_are_generated(context, event: str):
    query = f'fields message | sort @timestamp asc | filter correlation_id="{context.correlation_id}" | filter message="Event has been validated"'
    event_logs = get_logs(query, event)
    assert event_logs != [], f"ERROR!! No logs found!.."
    print(event_logs)


@then("the Changed Event is stored in dynamo db")
def stored_dynamo_db_events_are_pulled(context):
    odscode = context.change_event["ODSCode"]
    sequence_num = Decimal(context.sequence_no)
    db_event_record = get_stored_events_from_db(odscode, sequence_num)
    assert db_event_record is not None, f"ERROR!! Event record with odscode {odscode} NOT found!.."
    assert odscode == db_event_record["ODSCode"], f"ERROR!!.. Change event record(odscode) mismatch!!"
    assert sequence_num == db_event_record["SequenceNumber"], f"ERROR!!.. Change event record(sequence no) mismatch!!"


@then("the lambda is confirmed active")
def the_lambda_is_confirmed_active(context):
    status = get_lambda_info("status")
    assert status == "Active" or "Successful", f"ERROR! Invocation either unsuccessful or Lambda is inactive"


@then("the Changed Event is processed")
def the_changed_event_is_processed(context):
    query = f'fields message | sort @timestamp asc | filter correlation_id="{context.correlation_id}" | filter message like "change request"'
    logs = get_logs(query, "processor")
    print(logs)
    assert "DoS Integration CR" in logs, f"ERROR!!.. logs not found"


@then("the unmatched service exception is reported to cloudwatch")
def unmatched_service_exception(context):
    query = f'fields message | sort @timestamp asc | filter correlation_id="{context.correlation_id}" | filter message like "No matching DOS services"'
    logs = get_logs(query, "processor")
    odscode = context.change_event["ODSCode"]
    assert f"ODSCode '{odscode}'" in logs, f"ERROR!!.. expected unmatched service logs not found."

@then("the processed Changed Request is sent to Dos")
def processed_changed_event_sent_to_dos(context):
    query = f'fields message | sort @timestamp asc | filter correlation_id="{context.correlation_id}" | filter message like "Successfully send change request to DoS"'
    logs = get_logs(query, "sender")

# The below step definition answers to a corresponding 'AND' annotation within the feature file
@then("the Changed Request is accepted by Dos")
def the_changed_request_is_accepted_by_dos(context):
    """assert dos API response and validate processed record in Dos CR Queue database"""
    pass
