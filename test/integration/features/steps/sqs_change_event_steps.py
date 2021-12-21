from os import getenv
from behave import given, then, when, And
from features.utilities.utilities import get_response
from features.utilities.get_secrets import get_secret
import json


@given("a valid change request endpoint")
def a_valid_change_request_endpoint(context):
    pass


@when('a "{change_request_status}" change request is sent to the event sender')
def a_valid_change_request_is_sent_to_the_event_sender(context, change_request_status: str):
    response = get_response()
    secret = json.loads(get_secret())
    print(response.text)
    print(secret)
