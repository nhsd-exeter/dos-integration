from dataclasses import dataclass
from unittest.mock import patch

from pytest import fixture

from ..eventbridge_dlq_handler import lambda_handler

FILE_PATH = "application.eventbridge_dlq_handler.eventbridge_dlq_handler"


@fixture
def dead_letter_message():
    yield {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy0a...",
                "body": "Test message.",
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1545082649183",
                    "SenderId": "AIDAIENQZJOLO23YVJ4VO",
                    "ApproximateFirstReceiveTimestamp": "1545082649185",
                },
                "messageAttributes": {
                    "correlation-id": {
                        "stringValue": "059f36b4-87a3-44ab-83d2-661975830a7d",
                        "stringListValues": [],
                        "binaryListValues": [],
                        "dataType": "String",
                    }
                },
                "md5OfBody": "e4e68fb7bd0e697a0ae8f1bb342846b3",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:my-queue",
                "awsRegion": "us-east-2",
            }
        ]
    }


@fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = "event-processor"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:event-processor"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()


@patch(f"{FILE_PATH}.extract_body")
def test_lambda_handler(mock_extract_body, dead_letter_message, lambda_context):
    # Arrange
    extracted_body = {
        "correlation_id": "dummy_correlation_id",
        "dynamo_record_id": "adf382c13e1f265bbc5eb5fe59630390",
        "message_received": 1643272884341,
        "ods_code": "DUMMY",
    }
    mock_extract_body.return_value = extracted_body
    # Act
    lambda_handler(dead_letter_message, lambda_context)
    # Assert
    mock_extract_body.assert_called_once_with(dead_letter_message["Records"][0]["body"])
