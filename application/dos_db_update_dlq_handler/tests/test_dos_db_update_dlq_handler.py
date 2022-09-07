from dataclasses import dataclass
from os import environ
from unittest.mock import patch

from aws_embedded_metrics.logger.metrics_logger import MetricsLogger
from pytest import fixture

from ..dos_db_update_dlq_handler import lambda_handler

FILE_PATH = "application.dos_db_update_dlq_handler.dos_db_update_dlq_handler"


@fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = "dos-db-update-dlq-handler"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:dos-db-update-dlq-handler"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()


@patch(f"{FILE_PATH}.extract_body")
@patch.object(MetricsLogger, "put_metric")
@patch.object(MetricsLogger, "set_dimensions")
def test_lambda_handler(mock_put_metric, mock_set_dimentions, mock_extract_body, lambda_context):
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
    dead_letter_message = {
        "Records": [
            {
                "body": "Test message.",
                "messageAttributes": {
                    "correlation-id": {
                        "stringValue": "059f36b4-87a3-44ab-83d2-661975830a7d",
                        "stringListValues": [],
                        "binaryListValues": [],
                        "dataType": "String",
                    },
                    "error_msg_http_code": {
                        "stringValue": "401",
                        "stringListValues": [],
                        "binaryListValues": [],
                        "dataType": "String",
                    },
                    "error_msg": {
                        "stringValue": "My message",
                        "stringListValues": [],
                        "binaryListValues": [],
                        "dataType": "String",
                    },
                },
            }
        ]
    }
    environ["ENV"] = "test"
    mock_extract_body.return_value = extracted_body
    # Act
    lambda_handler(dead_letter_message, lambda_context)
    # Assert
    mock_extract_body.assert_called_once_with(dead_letter_message["Records"][0]["body"])
    # Clean up
    del environ["ENV"]
