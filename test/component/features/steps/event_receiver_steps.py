from json import loads
from os import getenv

from behave import given, then, when
from features.utilities.utilities import (
    compile_change_event,
    load_event_receiver_change_event,
    read_log_file,
    setup_change_event,
)
from requests import post


@given("a valid change event")
def a_valid_change_event(context):
    """Creates a valid change event"""
    context.change_event = setup_change_event()


@given("an invalid change event with incorrectly formatted event")
def an_invalid_change_event_invalid_format(context):
    """Creates an invalid change event that doesn't represent what API Gateway would give to lambda"""
    context.change_event = loads(setup_change_event()["body"])


@given("an invalid change event with incorrect service type")
def an_invalid_change_event_with_incorrect_service_type(context):
    """Creates an invalid change event with invalid service type"""
    change_event = load_event_receiver_change_event()
    change_event["body"]["ServiceType"] = "Anything"
    context.change_event = compile_change_event(change_event)


@given("an invalid change event with incorrect service sub type")
def an_invalid_change_event_with_incorrect_service_sub_type(context):
    """Creates an invalid change event with invalid service sub type"""
    change_event = load_event_receiver_change_event()
    change_event["body"]["ServiceSubType"] = "Anything"
    context.change_event = compile_change_event(change_event)


@given("an invalid change event with no ods code")
def an_invalid_change_event_with_no_ods_code(context):
    """Creates an invalid change event without an ods code"""
    change_event = load_event_receiver_change_event()
    del change_event["body"]["ODSCode"]
    context.change_event = compile_change_event(change_event)


@given("an invalid change event with incorrect length ods code")
def an_invalid_change_event_with_incorrect_length_ods_code(context):
    """Creates an invalid change event with invalid ods code length"""
    change_event = load_event_receiver_change_event()
    change_event["body"]["ODSCode"] = "ABCDEFGH"
    context.change_event = compile_change_event(change_event)


@given("an invalid change event with incorrect type ods code")
def an_invalid_change_event_with_incorrect_type_ods_code(context):
    """Creates an invalid change event with invalid ods code type"""
    change_event = load_event_receiver_change_event()
    change_event["body"]["ODSCode"] = 12345
    context.change_event = compile_change_event(change_event)


@when("a change event is sent to the event receiver")
def a_change_event_is_send_to_the_event_receiver(context):
    """Sends change event to Event Receiver lambda"""
    lambda_url = getenv("EVENT_RECEIVER_FUNCTION_URL")
    context.response = post(url=lambda_url, headers={"Content-Type": "application/json"}, json=context.change_event)


@then('the response has status code "{expected_status_code:d}" with message "{expected_message}"')
def the_response_body_contains_message(context, expected_status_code: int, expected_message: str):
    """Checks response has expected status code and message in response body"""
    actual_status_code = context.response.json()["statusCode"]
    assert expected_status_code == actual_status_code, f"Status code not as expected, Status Code: {actual_status_code}"
    response_message = loads(context.response.json()["body"])["message"]
    assert expected_message == response_message, f"Message not as expected, Message: {response_message}"


@then('the response has status code "{expected_status_code:d}" with error message "{expected_message}"')
def the_response_body_contains_error_message(context, expected_status_code: int, expected_message: str):
    """Checks response has expected status code and error message in response body"""
    actual_status_code = context.response.json()["statusCode"]
    assert expected_status_code == actual_status_code, f"Status code not as expected, Status Code: {actual_status_code}"
    error_message = loads(context.response.json()["body"])["message"]
    assert expected_message == error_message, f"Error Message not as expected, Error Message: {error_message}"


@then('the response is logged with status code "{expected_status_code:d}" and message "{expected_message}"')
def the_response_contained_in_logs(context, expected_status_code: int, expected_message: str):
    """Checks response is logged in log file"""
    log_file = read_log_file()
    assert (
        f"{expected_status_code}|{expected_message}" in log_file
    ), f"Log format not as expected, '{expected_status_code}|{expected_message}' not in logs"
