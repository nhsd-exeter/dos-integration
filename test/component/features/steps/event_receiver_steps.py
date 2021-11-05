from os import getenv

from behave import given, then, when
from features.utilities.utilities import load_json_file
from requests import post


@given("a valid change event")
def a_valid_change_event(context):
    """[summary]"""
    context.change_event = load_json_file("valid_change_event.json")


@given("an invalid change event")
def an_invalid_change_event(context):
    """[summary]"""
    context.change_event = load_json_file("invalid_change_event.json")


@when("a change event is sent to the event receiver")
def a_change_event_is_send_to_the_event_receiver(context):
    """Sends change event to Event Receiver lambda"""
    lambda_url = getenv("EVENT_RECEIVER_FUNCTION_URL")
    context.response = post(url=lambda_url, headers={"Content-Type": "application/json"}, json=context.change_event)


@then('the change event has status code "{status_code}"')
def the_change_event_has_status_code(context, status_code):
    """[summary]"""
    assert context.response.status_code == status_code
