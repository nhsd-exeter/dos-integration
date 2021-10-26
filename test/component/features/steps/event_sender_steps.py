from behave import given, then, when
from features.utilities.mockserver import MockServer
from features.utilities.utilities import load_json_file
from requests import post


@given("a valid change request endpoint")
def a_valid_change_request_endpoint(context):
    mockserver = MockServer()
    mockserver.reset_server()
    expectations = load_json_file("change_request_expectations.json")
    mockserver.put("/mockserver/expectation", expectations)
    mockserver.assert_status_code(201)


@when("a change request is sent to the event sender")
def a_change_request_is_sent_to_the_event_sender(context):
    lambda_url = "http://docker.for.mac.localhost:9000/2015-03-31/functions/function/invocations"
    change_request = load_json_file("valid_change_request.json")
    response = post(url=lambda_url, headers={"Content-Type": "application/json"}, json=change_request)
    assert response.status_code == 200


@then("a change request is received once")
def a_change_request_is_received_once(context):
    mockserver = MockServer()
    mockserver.put(
        "/mockserver/verify",
        {
            "httpRequest": {
                "method": "POST",
                "path": "/api/change-request",
            },
            "times": {"atLeast": 1, "atMost": 1},
        },
    )
    mockserver.assert_status_code(202)


@then("the expected change is received")
def the_expected_change_is_received(context):
    mockserver = MockServer()
    mockserver.put(
        "/retrieve?format=json&type=requests",
        {
            "method": "POST",
            "path": "/api/change-request",
        },
    )
    mockserver.assert_status_code(200)
