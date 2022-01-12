from os import getenv
from behave import given, then, when
from features.utilities.utilities import process_change_event, get_response, get_lambda_info
from features.utilities.log_stream import get_data_logs, get_logs
import json


@given("a valid change event endpoint")
def a_valid_change_event_endpoint(context):
    pass

@when('a "{valid}" change event is sent to the event procesor')
def a_valid_change_event_is_sent_to_the_event_procesor(context, valid: str):
    response = get_response(valid)
    assert response == "Change event received", "ERROR! Invalid Payload received.."

@when('an "{invalid}" change event is processed')
def an_invalid_change_event_is_processed(context, invalid: str):
    pass
    # response = get_response(invalid)
    # assert response['Message'] != "Change event received", "ERROR! Payload received not invalid.."

@when('an "{expected}" change event is sent to the event procesor')
def an_expected_change_event_is_sent_to_the_event_procesor(context, expected: str):
    response = get_response(expected)
    assert response == "Change event received", "ERROR! Invalid Payload received.."

@then('the event processor logs are generated')
def the_event_processor_logs_are_generated(context):
    logs = get_logs(seconds_ago=120)
    print(logs)

@then('the lambda is confirmed active')
def the_lambda_is_confirmed_active(context):
    status = get_lambda_info("status")
    assert status == "Active" or "Successful", "ERROR! Invocation either unsuccessful or Lambda is inactive"
    print(status)
    print(status)
