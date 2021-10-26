from behave import given, then, when
from features.utilities.mockserver import MockServer
from features.utilities.utilities import load_json_file
from requests import post


@given("a valid change request endpoint")
def step_impl(context):
    mockserver = MockServer()
    mockserver.reset_server()
    expectations = load_json_file("change_request_expectations.json")
    response = mockserver.put("/mockserver/expectation", expectations)
    assert response.status_code == 201


@when("a change request is sent to the event sender")
def step_impl(context):
    lambda_url = "http://docker.for.mac.localhost:9000/2015-03-31/functions/function/invocations"
    change_request = load_json_file("valid_change_request.json")
    response = post(url=lambda_url, headers={"Content-Type": "application/json"}, json=change_request)
    assert response.status_code == 200


@then("a change request is received once")
def step_impl(context):
    mockserver = MockServer()
    response = mockserver.put(
        "/mockserver/verify",
        {
            "httpRequest": {
                "method": "POST",
                "path": "/api/change-request",
            },
            "times": {"atLeast": 1, "atMost": 1},
        },
    )
    assert response.status_code == 202


@then("the expected change is received")
def step_impl(context):
    mockserver = MockServer()
    response = mockserver.put(
        "/retrieve?format=json&type=requests",
        {
            "method": "POST",
            "path": "/api/change-request",
        },
    )
    print(response.json())
    assert response.status_code == 200
