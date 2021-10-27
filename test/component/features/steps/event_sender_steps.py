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
def a_valid_change_request_is_sent_to_the_event_sender(context, change_request_status):
    """Sends change event to Event Sender lambda"""
    lambda_url = getenv("EVENT_SENDER_FUNCTION_URL")
    change_request_file_name = get_change_request_name(change_request_status)
    change_request = load_json_file(change_request_file_name)
    response = post(url=lambda_url, headers={"Content-Type": "application/json"}, json=change_request)
    assert response.status_code == 200


@then('a change request is received "{number_of_times}" times')
def a_change_request_is_received_x_times(context, number_of_times):
    """Confirms number of times a change request has been received"""
    number_of_times = int(number_of_times)
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


@then('the change request has status code "{status_code}"')
def the_change_request_has_status_code_x(context, status_code):
    """Checks status code from mock server is as expected"""
    status_code = int(status_code)
    mockserver = MockServer()
    mockserver.put("/retrieve?format=json&type=request_responses", body={})
    mockserver.assert_status_code(200)
    requests = mockserver.response.json()
    assert requests[0]["httpResponse"]["statusCode"] == status_code


@then('the response "{response_status}" is logged and has status code "{status_code}"')
def the_response_is_logged(context, response_status, status_code):
    """Checks if expected criteria is stored in the log files"""
    change_request_file_name = get_change_request_name(response_status)
    change_request = load_json_file(change_request_file_name)
    file_path = "../../build/automation/tmp/log_file.txt"
    with open(file_path, "r", encoding="utf-8") as file:
        log_file = file.read()
    if response_status == "Success":
        assert (
            f"CHANGE_REQUEST|{response_status}|{status_code}|"
            + "{'dosChanges': [{'changeId': 'Change_ID_1_here'}, {'changeId': 'Change_ID_2_here'}]}"
            in log_file
        ), "Log Format not found"
    elif response_status == "Failure":
        assert "CHANGE_REQUEST|Failure to log response" in log_file, "Log Format not found"
    assert str(change_request) in log_file
