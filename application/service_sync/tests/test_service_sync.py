from dataclasses import dataclass
from os import environ
from unittest.mock import MagicMock, patch

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from pytest import fixture

from ..service_sync import add_success_metric, lambda_handler, remove_sqs_message_from_queue, set_up_logging
from common.types import UpdateRequest, UpdateRequestMetadata, UpdateRequestQueueItem

FILE_PATH = "application.service_sync.service_sync"

SERVICE_ID = "1"
CHANGE_EVENT = {"ODSCode": "12345"}
RECIPIENT_ID = "recipient_id"
UPDATE_REQUEST_QUEUE_ITEM = UpdateRequestQueueItem(
    update_request=UpdateRequest(change_event=CHANGE_EVENT, service_id=SERVICE_ID),
    recipient_id=RECIPIENT_ID,
    metadata=UpdateRequestMetadata(
        dynamo_record_id="dynamo_record_id",
        correlation_id="correlation_id",
        message_group_id="message_group_id",
        ods_code="ods_code",
        message_deduplication_id="message_deduplication_id",
        message_received=123456789,
    ),
)


@fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = "service-sync"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:service-sync"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()


@patch(f"{FILE_PATH}.add_success_metric")
@patch(f"{FILE_PATH}.remove_sqs_message_from_queue")
@patch(f"{FILE_PATH}.update_dos_data")
@patch(f"{FILE_PATH}.compare_nhs_uk_and_dos_data")
@patch(f"{FILE_PATH}.get_dos_service_and_history")
@patch(f"{FILE_PATH}.NHSEntity")
@patch(f"{FILE_PATH}.set_up_logging")
def test_lambda_handler(
    mock_set_up_logging: MagicMock,
    mock_nhs_entity: MagicMock,
    mock_get_dos_service_and_history: MagicMock,
    mock_compare_nhs_uk_and_dos_data: MagicMock,
    mock_update_dos_data: MagicMock,
    mock_remove_sqs_message_from_queue: MagicMock,
    mock_add_success_metric: MagicMock,
    lambda_context: LambdaContext,
):
    # Arrange
    dos_service = MagicMock()
    service_histories = MagicMock()
    nhs_entity = MagicMock()
    mock_nhs_entity.return_value = nhs_entity
    mock_get_dos_service_and_history.return_value = dos_service, service_histories
    # Act
    response = lambda_handler(event=UPDATE_REQUEST_QUEUE_ITEM, context=lambda_context)
    # Assert
    assert {"message": "The change event has been processed successfully"} == response
    mock_set_up_logging.assert_called_once_with(UPDATE_REQUEST_QUEUE_ITEM)
    mock_nhs_entity.assert_called_once_with(CHANGE_EVENT)
    mock_get_dos_service_and_history.assert_called_once_with(service_id=SERVICE_ID)
    mock_compare_nhs_uk_and_dos_data.assert_called_once_with(
        dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories
    )
    mock_update_dos_data.assert_called_once_with(
        changes_to_dos=mock_compare_nhs_uk_and_dos_data(),
        service_id=SERVICE_ID,
        service_histories=mock_compare_nhs_uk_and_dos_data().service_histories,
    )
    mock_remove_sqs_message_from_queue.assert_called_once_with(event=UPDATE_REQUEST_QUEUE_ITEM)
    mock_add_success_metric.assert_called_once_with(event=UPDATE_REQUEST_QUEUE_ITEM)


@patch.object(Logger, "append_keys")
@patch.object(Logger, "set_correlation_id")
def test_set_up_logging(mock_set_correlation_id: MagicMock, mock_append_keys: MagicMock):
    # Act
    set_up_logging(UPDATE_REQUEST_QUEUE_ITEM)
    # Assert
    mock_set_correlation_id.assert_called_once_with("correlation_id")
    mock_append_keys.assert_called_once_with(ods_code=CHANGE_EVENT["ODSCode"], service_id=SERVICE_ID)


@patch.object(Logger, "info")
@patch(f"{FILE_PATH}.client")
def test_remove_sqs_message_from_queue(mock_client: MagicMock, mock_logger_info: MagicMock):
    # Arrange
    environ["UPDATE_REQUEST_QUEUE_URL"] = update_request_queue_url = "update_request_queue_url"
    # Act
    remove_sqs_message_from_queue(UPDATE_REQUEST_QUEUE_ITEM)
    # Assert
    mock_client.assert_called_once_with("sqs")
    mock_client.return_value.delete_message.assert_called_once_with(
        QueueUrl=update_request_queue_url, ReceiptHandle=RECIPIENT_ID
    )
    mock_logger_info.assert_called_once_with("Removed SQS message from queue", extra={"receipt_handle": RECIPIENT_ID})
    # Cleanup
    del environ["UPDATE_REQUEST_QUEUE_URL"]


def test_add_success_metric():
    # Arrange
    environ["ENV"] = "environment"
    # Act
    add_success_metric(UPDATE_REQUEST_QUEUE_ITEM)
    # Cleanup
    del environ["ENV"]
