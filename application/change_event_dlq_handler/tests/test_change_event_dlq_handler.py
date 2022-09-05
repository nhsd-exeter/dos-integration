from dataclasses import dataclass
from unittest.mock import patch

from aws_embedded_metrics.logger.metrics_logger import MetricsLogger
from pytest import fixture

from ..change_event_dlq_handler import lambda_handler

FILE_PATH = "application.change_event_dlq_handler.change_event_dlq_handler"


@fixture
def dead_letter_change_event():
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
        function_name: str = "service-matcher"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:service-matcher"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()


@patch(f"{FILE_PATH}.extract_body")
@patch(f"{FILE_PATH}.add_change_event_to_dynamodb")
@patch.object(MetricsLogger, "put_metric")
@patch.object(MetricsLogger, "set_dimensions")
def test_lambda_handler(
    mock_put_metric,
    mock_set_dimensions,
    mock_add_change_event_to_dynamodb,
    mock_extract_body,
    dead_letter_change_event,
    lambda_context,
):
    # Arrange
    extracted_body = "Test message1."
    mock_extract_body.return_value = extracted_body
    # Act
    lambda_handler(dead_letter_change_event, lambda_context)
    # Assert
    mock_extract_body.assert_called_once_with(dead_letter_change_event["Records"][0]["body"])
    expected_timestamp = int(dead_letter_change_event["Records"][0]["attributes"]["SentTimestamp"])
    mock_add_change_event_to_dynamodb.assert_called_once_with(extracted_body, None, expected_timestamp)
