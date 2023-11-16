from os import environ
from unittest.mock import MagicMock, patch

from aws_lambda_powertools.utilities.typing import LambdaContext

from application.dos_db_update_dlq_handler.dos_db_update_dlq_handler import lambda_handler

FILE_PATH = "application.dos_db_update_dlq_handler.dos_db_update_dlq_handler"


@patch(f"{FILE_PATH}.extract_body")
def test_lambda_handler(mock_extract_body: MagicMock, lambda_context: LambdaContext):
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
            },
        ],
    }
    environ["ENV"] = "test"
    mock_extract_body.return_value = extracted_body
    # Act
    lambda_handler(dead_letter_message, lambda_context)
    # Assert
    mock_extract_body.assert_called_once_with(dead_letter_message["Records"][0]["body"])
    # Clean up
    del environ["ENV"]
