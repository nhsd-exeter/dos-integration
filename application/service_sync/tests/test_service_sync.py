from json import dumps
from os import environ
from unittest.mock import MagicMock, patch

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from application.service_sync.service_sync import lambda_handler, remove_sqs_message_from_queue
from common.types import UpdateRequest

FILE_PATH = "application.service_sync.service_sync"

SERVICE_ID = "1"
CHANGE_EVENT = {"ODSCode": "12345"}
RECEIPT_HANDLE = "receipt_handle"
MESSAGE_RECEIVED = "1683017134"

SQS_EVENT = {
    "Records": [
        {
            "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
            "receiptHandle": RECEIPT_HANDLE,
            "body": dumps(UpdateRequest(change_event=CHANGE_EVENT, service_id=SERVICE_ID)),
            "attributes": {
                "ApproximateReceiveCount": "1",
                "SentTimestamp": "1642619743522",
                "SenderId": "AIDAIENQZJOLO23YVJ4VO",
                "ApproximateFirstReceiveTimestamp": "1545082649185",
            },
            "messageAttributes": {
                "correlation-id": {"stringValue": "1", "dataType": "String"},
                "sequence-number": {"stringValue": "1", "dataType": "Number"},
                "message_received": {"stringValue": MESSAGE_RECEIVED, "dataType": "Number"},
            },
            "md5OfBody": "e4e68fb7bd0e697a0ae8f1bb342846b3",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:my-queue",
            "awsRegion": "us-east-2",
        },
    ],
}


@patch(f"{FILE_PATH}.check_and_remove_pending_dos_changes")
@patch(f"{FILE_PATH}.remove_sqs_message_from_queue")
@patch(f"{FILE_PATH}.update_dos_data")
@patch(f"{FILE_PATH}.compare_nhs_uk_and_dos_data")
@patch(f"{FILE_PATH}.get_dos_service_and_history")
@patch(f"{FILE_PATH}.NHSEntity")
def test_lambda_handler(
    mock_nhs_entity: MagicMock,
    mock_get_dos_service_and_history: MagicMock,
    mock_compare_nhs_uk_and_dos_data: MagicMock,
    mock_update_dos_data: MagicMock,
    mock_remove_sqs_message_from_queue: MagicMock,
    mock_check_and_remove_pending_dos_changes: MagicMock,
    lambda_context: LambdaContext,
):
    # Arrange
    environ["ENV"] = "environment"
    dos_service = MagicMock()
    service_histories = MagicMock()
    nhs_entity = MagicMock()
    mock_nhs_entity.return_value = nhs_entity
    mock_get_dos_service_and_history.return_value = dos_service, service_histories
    # Act
    lambda_handler(event=SQS_EVENT, context=lambda_context)
    # Assert
    mock_check_and_remove_pending_dos_changes.assert_called_once_with(SERVICE_ID)
    mock_nhs_entity.assert_called_once_with(CHANGE_EVENT)
    mock_get_dos_service_and_history.assert_called_once_with(service_id=int(SERVICE_ID))
    mock_compare_nhs_uk_and_dos_data.assert_called_once_with(
        dos_service=dos_service,
        nhs_entity=nhs_entity,
        service_histories=service_histories,
    )
    mock_update_dos_data.assert_called_once_with(
        changes_to_dos=mock_compare_nhs_uk_and_dos_data(),
        service_id=int(SERVICE_ID),
        service_histories=mock_compare_nhs_uk_and_dos_data().service_histories,
    )
    mock_remove_sqs_message_from_queue.assert_called_once_with(receipt_handle=RECEIPT_HANDLE)
    # Cleanup
    del environ["ENV"]


@patch(f"{FILE_PATH}.check_and_remove_pending_dos_changes")
@patch.object(Logger, "exception")
@patch(f"{FILE_PATH}.remove_sqs_message_from_queue")
@patch(f"{FILE_PATH}.update_dos_data")
@patch(f"{FILE_PATH}.compare_nhs_uk_and_dos_data")
@patch(f"{FILE_PATH}.get_dos_service_and_history")
@patch(f"{FILE_PATH}.NHSEntity")
def test_lambda_handler_exception(
    mock_nhs_entity: MagicMock,
    mock_get_dos_service_and_history: MagicMock,
    mock_compare_nhs_uk_and_dos_data: MagicMock,
    mock_update_dos_data: MagicMock,
    mock_remove_sqs_message_from_queue: MagicMock,
    mock_logger_exception: MagicMock,
    mock_check_and_remove_pending_dos_changes: MagicMock,
    lambda_context: LambdaContext,
):
    # Arrange
    nhs_entity = MagicMock()
    mock_nhs_entity.return_value = nhs_entity
    mock_get_dos_service_and_history.side_effect = Exception("Error")
    # Act
    lambda_handler(event=SQS_EVENT, context=lambda_context)
    # Assert
    mock_check_and_remove_pending_dos_changes.assert_called_once_with(SERVICE_ID)
    mock_nhs_entity.assert_called_once_with(CHANGE_EVENT)
    mock_get_dos_service_and_history.assert_called_once_with(service_id=int(SERVICE_ID))
    mock_compare_nhs_uk_and_dos_data.assert_not_called()
    mock_update_dos_data.assert_not_called()
    mock_remove_sqs_message_from_queue.assert_not_called()
    mock_logger_exception.assert_called_once_with(
        "Error processing update request",
        environment="local",
        cloudwatch_metric_filter_matching_attribute="UpdateRequestError",
    )


@patch.object(Logger, "info")
@patch(f"{FILE_PATH}.client")
def test_remove_sqs_message_from_queue(mock_client: MagicMock, mock_logger_info: MagicMock):
    # Arrange
    environ["UPDATE_REQUEST_QUEUE_URL"] = update_request_queue_url = "update_request_queue_url"
    # Act
    remove_sqs_message_from_queue(receipt_handle=RECEIPT_HANDLE)
    # Assert
    mock_client.assert_called_once_with("sqs")
    mock_client.return_value.delete_message.assert_called_once_with(
        QueueUrl=update_request_queue_url,
        ReceiptHandle=RECEIPT_HANDLE,
    )
    mock_logger_info.assert_called_once_with("Removed SQS message from queue", receipt_handle=RECEIPT_HANDLE)
    # Cleanup
    del environ["UPDATE_REQUEST_QUEUE_URL"]
