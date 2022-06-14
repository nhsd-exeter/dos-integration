from dataclasses import dataclass
from json import dumps

import pytest

from ..dos_api_gateway import lambda_handler


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
            {
                "reference": "1",
                "system": "DoS Integration",
                "message": "Test message 153181659229",
                "service_id": "49016",
                "changes": {"website": "https://www.google.pl", "public_name": "Test Name"},
            },
            201,
            dumps({"dosChanges": [{"changeId": "1" * 9}, {"changeId": "2" * 9}]}),
        ),
        ({}, 200, "Change Request is empty"),
        (
            {
                "reference": "bad request dummy_correlation_id",
                "system": "DoS Integration",
                "message": "Test message 153181659229",
                "service_id": "49016",
                "changes": {"website": "https://www.google.pl", "public_name": "Test Name"},
            },
            400,
            "Fake Bad Request trigged by correlation-id",
        ),
    ],
)
def test_lambda_handler(lambda_context, change_request, expected_response_status_code, expected_response_body):
    # Arrange
    lambda_event = {"body": dumps(change_request)}
    # Act
    response = lambda_handler(lambda_event, lambda_context)
    # Assert
    assert response["statusCode"] == expected_response_status_code
    assert response["body"] == expected_response_body
