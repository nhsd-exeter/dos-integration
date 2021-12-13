from os import getenv

from behave import given, then, when
from features.utilities.mockserver import MockServer
from features.utilities.utilities import get_change_request_name, load_json_file
from requests import post


@given("a valid change request endpoint")
def a_valid_change_request_endpoint(context):
    """Sets up mockserver with expectations"""
    mockserver = MockServer()
    mockserver.reset_server()
    expectations = load_json_file("change_request_expectations.json")
    mockserver.put("/mockserver/expectation", expectations)
    mockserver.assert_status_code(201)


@when('a "{change_request_status}" change request is sent to the event sender')
def a_valid_change_request_is_sent_to_the_event_sender(context, change_request_status: str):
    """Sends change event to Event Sender lambda"""
    lambda_url = getenv("EVENT_SENDER_FUNCTION_URL")
    change_request_file_name = get_change_request_name(change_request_status)
    change_request = load_json_file(change_request_file_name)
    response = post(url=lambda_url, headers={"Content-Type": "application/json"}, json=change_request)
    assert response.status_code == 200


@then('a change request is received "{number_of_times:d}" times')
def a_change_request_is_received_x_times(context, number_of_times: int):
    """Confirms number of times a change request has been received"""
    mockserver = MockServer()
    mockserver.put(
        "/mockserver/verify",
        {
            "httpRequest": {
                "method": "POST",
                "path": "/api/change-request",
            },
            "times": {"atLeast": number_of_times, "atMost": number_of_times},
        },
    )
    mockserver.assert_status_code(202)


@then('the change request has status code "{expected_status_code:d}"')
def the_change_request_has_status_code_x(context, expected_status_code: int):
    """Checks status code from mock server is as expected"""
    mockserver = MockServer()
    mockserver.put("/retrieve?format=json&type=request_responses", body={})
    mockserver.assert_status_code(200)
    requests = mockserver.response.json()
    actual_status_code = requests[0]["httpResponse"]["statusCode"]
    assert (
        expected_status_code == actual_status_code
    ), f"Status code not as expected, Expected: {expected_status_code}, Actual {actual_status_code}"
