from os import getenv
from behave import given, then, when
from features.utilities.utilities import get_response, get_lambda_info, purge_queue, process_change_event
from features.utilities.log_stream import get_data_logs, get_logs, get_logs_within_time_frame
import json


@given("a valid change event endpoint")
def a_valid_change_event_endpoint(context):
    pass

@given(" the endpoint connection is established")
def the_endpoint_connection_is_established(context):
    pass

@when('a "{valid}" change event with correlation id "{corrid}" is sent to the event procesor')
def a_valid_change_event_with_correlation_id_is_sent_to_the_event_procesor(context, valid: str, corrid: str):
    response = process_change_event(valid, corrid)
    message = response.json()
    assert response.status_code == 200, f"Status code not as expected.. Status code: {response.status_code} Error: {message}"

@when('an "{invalid}" change event with correlation id "{corrid}" is processed')
def an_invalid_change_event_with_correlation_id_is_processed(context, invalid: str, corrid: str):
    response = process_change_event(invalid, corrid)
    message = response.json()
    assert response.status_code == 200, f"Status code not as expected.. Status code: {response.status_code} Error: {message}"
    purge_queue()

@when('an "{expected}" change event is sent to the event procesor')
def an_expected_change_event_is_sent_to_the_event_procesor(context, expected: str):
    response = get_response(expected)
    assert response == "Change event received", "ERROR! Invalid Payload received.."

@then('the event processor logs are generated')
def the_event_processor_logs_are_generated(context):
    logs = get_logs(seconds_ago=120)
    assert logs != [], "ERROR!! No logs found!.."

    print(logs)

@then('the lambda is confirmed active')
def the_lambda_is_confirmed_active(context):
    status = get_lambda_info("status")
    assert status == "Active" or "Successful", "ERROR! Invocation either unsuccessful or Lambda is inactive"
    print(status)
    print(status)
