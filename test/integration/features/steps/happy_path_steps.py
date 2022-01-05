from os import getenv
from behave import given, then, when
from features.utilities.utilities import process_change_event
# from features.utilities.get_secrets import get_secret
# import json


@given("a valid change request endpoint")
def a_valid_change_request_endpoint(context):
    pass


@when('a valid change request is sent to the event sender')
def a_valid_change_request_is_sent_to_the_event_sender(context):
    response = process_change_event()
    assert response['Message'] == "Change event received", "ERROR! Invalid Payload received.."
