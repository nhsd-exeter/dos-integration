from os import getenv
from behave import given, then, when
from features.utilities.utils import (
    get_response,
    get_lambda_info,
    debug_purge_queue,
    process_payload,
    get_stored_events_from_db,
    get_payload,
)
from features.utilities.change_events import get_change_event_string, get_change_event_dict
from features.utilities.log_stream import get_logs
import json


@given("a valid change event is provided")
def a_change_event_is_provided(context):
    """Creates a valid change event"""
    context.change_event = get_change_event_string()


@given("a change event with invalid ODSCode is provided")
def a_change_event_is_provided(context):
    """Creates a valid change event"""
    context.change_event = get_change_event_dict()
    context.change_event["ODSCode"] = "FAKE5"


@given("a change event with invalid OrganisationSubType is provided")
def a_change_event_is_provided(context):
    """Creates a valid change event"""
    context.change_event = get_change_event_dict()
    context.change_event["OrganisationSubType"] = "com"


@when("the change event is sent to the event processor")
def the_change_event_is_processed(context):
    context.response = process_payload(context.change_event)
    context.correlation_id = context.response.headers["x-amz-apigw-id"]
    # debug_purge_queue()
    message = context.response.json()
    assert (
        context.response.status_code == 200
    ), f"Status code not as expected.. Status code: {context.response.status_code} Error: {message}"


@when('a "{valid}" change event with sequence id "{corrid}" is sent to the event procesor')
def a_valid_change_event_with_seq_id_is_processed(context, valid: str, corrid: str):
    response = process_payload(valid, corrid)
    message = response.json()
    assert (
        response.status_code == 200
    ), f"Status code not as expected.. Status code: {response.status_code} Error: {message}"


@when('an "{invalid}" change event with sequence id "{corrid}" is processed')
def an_invalid_change_event_with_seq_id_is_processed(context, invalid: str, corrid: str):
    response = process_payload(invalid, corrid)
    message = response.json()
    assert (
        response.status_code == 200
    ), f"Status code not as expected.. Status code: {response.status_code} Error: {message}"
    debug_purge_queue()


@when('an "{expected}" change event is sent to the event procesor')
def an_expected_change_event_is_sent_to_the_event_procesor(context, expected: str):
    response = get_response(expected)
    assert response == "Change event received", f"ERROR! Invalid Payload received.."


@then("the processor lambda logs are generated")
def the_processor_lambda_logs_are_generated(context):
    query = f'fields message | sort @timestamp asc | filter correlation_id="{context.correlation_id}" | filter message="Event has been validated"'
    logs = get_logs(query)
    assert logs != [], f"ERROR!! No logs found!.."


@then('the "{valid}" payload with sequence id "{seqid}" is stored in dynamo db')
def stored_dynamo_db_events_are_pulled(context, seqid: str, valid: str):
    db_event_record = get_stored_events_from_db(seqid)
    expected_payload = json.loads(get_payload(valid))
    assert db_event_record != [], f"ERROR!! Event record NOT found!.."
    assert expected_payload["ODSCode"] == db_event_record["ODSCode"], f"ERROR!!.. Change event record mismatch!!"
    assert (
        expected_payload["SequenceNumber"] == db_event_record["SequenceNumber"]
    ), f"ERROR!!.. Change event record mismatch!!"


@then("the lambda is confirmed active")
def the_lambda_is_confirmed_active(context):
    status = get_lambda_info("status")
    assert status == "Active" or "Successful", f"ERROR! Invocation either unsuccessful or Lambda is inactive"
