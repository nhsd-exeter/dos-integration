from os import getenv

from behave import given, then, when
from features.utilities.utilities import load_json_file, read_log_file
from requests import post
from json import loads

VALID_CHANGE_EVENT_FILE_NAME = "valid_change_event.json"


@given("a valid change event")
def a_valid_change_event(context):
    """[summary]"""
    context.change_event = load_json_file(VALID_CHANGE_EVENT_FILE_NAME)


@given("an invalid change event with incorrectly formatted event")
def an_invalid_change_event_invalid_format(context):
    """[summary]"""
    context.change_event = load_json_file(VALID_CHANGE_EVENT_FILE_NAME)["body"]


@given("an invalid change event with incorrect organisation type")
def an_invalid_change_event_with_incorrect_organisation_type(context):
    """[summary]"""
    context.change_event = load_json_file(VALID_CHANGE_EVENT_FILE_NAME)
    context.change_event["body"]["OrganisationType"] = "Anything"


@given("an invalid change event with no ods code")
def an_invalid_change_event_with_no_ods_code(context):
    """[summary]"""
    context.change_event = load_json_file(VALID_CHANGE_EVENT_FILE_NAME)
    del context.change_event["body"]["ODSCode"]


@given("an invalid change event with incorrect length ods code")
def an_invalid_change_event_with_incorrect_length_ods_code(context):
    """[summary]"""
    context.change_event = load_json_file(VALID_CHANGE_EVENT_FILE_NAME)
    context.change_event["body"]["ODSCode"] = "ABCDEFGH"


@given("an invalid change event with incorrect type ods code")
def an_invalid_change_event_with_incorrect_type_ods_code(context):
    """[summary]"""
    context.change_event = load_json_file(VALID_CHANGE_EVENT_FILE_NAME)
    context.change_event["body"]["ODSCode"] = 12345


@when("a change event is sent to the event receiver")
def a_change_event_is_send_to_the_event_receiver(context):
    """Sends change event to Event Receiver lambda"""
    lambda_url = getenv("EVENT_RECEIVER_FUNCTION_URL")
    context.response = post(url=lambda_url, headers={"Content-Type": "application/json"}, json=context.change_event)


@then('the response has status code "{expected_status_code:d}" with message "{expected_message}"')
def the_response_body_contains_message(context, expected_status_code: str, expected_message: str):
    """[summary]"""
    actual_status_code = context.response.json()["statusCode"]
    assert expected_status_code == actual_status_code, f"Status code not as expected, Status Code: {actual_status_code}"
    response_message = loads(context.response.json()["body"])["message"]
    assert expected_message == response_message, f"Message not as expected, Message: {response_message}"


@then('the response has status code "{expected_status_code:d}" with error message "{expected_message}"')
def the_response_body_contains_error_message(context, expected_status_code: str, expected_message: str):
    """[summary]"""
    actual_status_code = context.response.json()["statusCode"]
    assert expected_status_code == actual_status_code, f"Status code not as expected, Status Code: {actual_status_code}"
    error_message = loads(context.response.json()["errorMessage"])["message"]
    assert expected_message == error_message, f"Error Message not as expected, Error Message: {error_message}"


@then('the response is logged with status code "{expected_status_code:d}" and message "{expected_message}"')
def the_response_contained_in_logs(context, expected_status_code: str, expected_message: str):
    """[summary]"""
    log_file = read_log_file()
    assert (
        f"{expected_status_code}|{expected_message}" in log_file
    ), f"Log format not as expected, '{expected_status_code}|{expected_message}' not in logs"
