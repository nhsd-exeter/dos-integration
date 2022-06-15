from dataclasses import dataclass
from json import dumps
from os import environ

import pytest

from ..dos_api_gateway import lambda_handler

FILE_PATH = "application.dos_api_gateway.dos_api_gateway"
COMMON_CHANGE_REQUEST_KEYS = {
    "system": "DoS Integration",
    "message": "Test message 153181659229",
    "service_id": "49016",
    "changes": {"website": "https://www.google.pl", "public_name": "Test Name"},
}
STANDARD_CHANGE_REQUEST = {"reference": "1"} | COMMON_CHANGE_REQUEST_KEYS
BAD_CHANGE_REQUEST = {"reference": "bad request dummy_correlation_id"} | COMMON_CHANGE_REQUEST_KEYS


@pytest.fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = "event-sender"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:event-sender"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()


@pytest.mark.parametrize(
    "change_request, expected_response_status_code, expected_response_body",
    [
        (
            STANDARD_CHANGE_REQUEST,
            201,
            dumps({"dosChanges": [{"changeId": "1" * 9}, {"changeId": "2" * 9}]}),
        ),
        ({}, 200, "Change Request is empty"),
        (
            BAD_CHANGE_REQUEST,
            400,
            "Fake Bad Request trigged by correlation-id",
        ),
    ],
)
def test_lambda_handler(lambda_context, change_request, expected_response_status_code, expected_response_body):
    # Arrange
    lambda_event = {"body": dumps(change_request)}
    environ["SLEEP_TIME"] = "0"
    # Act
    response = lambda_handler(lambda_event, lambda_context)
    # Assert
    assert response["statusCode"] == expected_response_status_code
    assert response["body"] == expected_response_body
    # Clean up
    del environ["SLEEP_TIME"]


def test_lambda_handler_chaos_mode(lambda_context):
    # Arrange
    lambda_event = {"body": dumps(STANDARD_CHANGE_REQUEST)}
    environ["SLEEP_TIME"] = "0"
    environ["CHAOS_MODE"] = "true"
    # Act
    response = lambda_handler(lambda_event, lambda_context)
    # Assert
    assert response["statusCode"] == 500
    assert response["body"] == "Chaos mode is enabled"
    # Clean up
    del environ["SLEEP_TIME"]
    del environ["CHAOS_MODE"]


def test_lambda_handler_no_changes(lambda_context):
    # Arrange
    change_request = STANDARD_CHANGE_REQUEST.copy()
    del change_request["changes"]
    lambda_event = {"body": dumps(change_request)}
    print(lambda_event)
    environ["SLEEP_TIME"] = "0"
    # Act
    response = lambda_handler(lambda_event, lambda_context)
    # Assert
    assert response["statusCode"] == 500
    assert response["body"] == "No changes found in change request"
    # Clean up
    del environ["SLEEP_TIME"]
