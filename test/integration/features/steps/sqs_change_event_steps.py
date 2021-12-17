from os import getenv
from behave import given, then, when
from features.utilities.utilities import get_response


@given("a valid change request endpoint")
def a_valid_change_request_endpoint(context):
    pass


@when('a "{change_request_status}" change request is sent to the event sender')
def a_valid_change_request_is_sent_to_the_event_sender(context, change_request_status: str):
    response = get_response()
    print(response.text)
