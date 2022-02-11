from dataclasses import dataclass
from unittest.mock import patch

from pytest import fixture

from ..eventbridge_dlq_handler import lambda_handler, handle_msg_attributes

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
                    "ERROR_MESSAGE": {
                        "stringValue": "ApiDestination returned HTTP status 400 with payload: Dummy",
                        "stringListValues": [],
                        "binaryListValues": [],
                        "dataType": "String",
                    },
                    "ERROR_CODE": {
                        "stringValue": "SDK_CLIENT_ERROR",
                        "stringListValues": [],
                        "binaryListValues": [],
                        "dataType": "String",
                    },
                    "RULE_ARN": {
                        "stringValue": "arn:aws:events:eu:0:rule/dummy-eventbridge-bus/dummy-change-request-rule",
                        "stringListValues": [],
                        "binaryListValues": [],
                        "dataType": "String",
                    },
                    "TARGET_ARN": {
                        "stringValue": "arn:aws:events:eu:0:api-destination/dummy-dos-api-gateway-api-destination/abc",
                        "stringListValues": [],
                        "binaryListValues": [],
                        "dataType": "String",
                    },
                },
                "md5OfBody": "e4e68fb7bd0e697a0ae8f1bb342846b3",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:eventbridge-dlq-queue",
                "awsRegion": "us-east-2",
            }
        ]
    }


@fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = "eventbridge-dlq-handler"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:eventbridge-dlq-handler"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()


@patch(f"{FILE_PATH}.extract_body")
def test_lambda_handler(mock_extract_body, dead_letter_message, lambda_context):
    # Arrange
    change_request = {
        "reference": "Dummy correlation id",
        "system": "DoS Integration",
        "message": "DoS Integration CR. correlation-id: Dummy correlation id",
        "service_id": "63805",
        "changes": {"phone": None},
    }
    extracted_body = {
        "correlation_id": "dummy_correlation_id",
        "dynamo_record_id": "adf382c13e1f265bbc5eb5fe59630390",
        "message_received": 1643272884341,
        "ods_code": "DUMMY",
        "change_payload": change_request,
    }
    mock_extract_body.return_value = extracted_body
    # Act
    lambda_handler(dead_letter_message, lambda_context)
    # Assert
    mock_extract_body.assert_called_once_with(dead_letter_message["Records"][0]["body"])


def test_handle_msg_attributes(dead_letter_message):
    msg_attributes = dead_letter_message["Records"][0]["messageAttributes"]

    attributes = handle_msg_attributes(msg_attributes=msg_attributes)
    assert attributes["error_msg"] == msg_attributes["ERROR_MESSAGE"]["stringValue"]
    assert attributes["error_msg_http_code"] == 400
    assert attributes["error_code"] == msg_attributes["ERROR_CODE"]["stringValue"]
    assert attributes["rule_arn"] == msg_attributes["RULE_ARN"]["stringValue"]
    assert attributes["target_arn"] == msg_attributes["TARGET_ARN"]["stringValue"]
