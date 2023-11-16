import hashlib
from json import dumps
from os import environ
from typing import Any
from unittest.mock import patch

import pytest
from aws_lambda_powertools.logging import Logger

from application.common.types import HoldingQueueChangeEventItem
from application.conftest import PHARMACY_STANDARD_EVENT, dummy_dos_service
from application.service_matcher.service_matcher import lambda_handler, send_update_requests
from common.nhs import NHSEntity

FILE_PATH = "application.service_matcher.service_matcher"


def _get_message_attributes(
    correlation_id: str,
    message_received: int,
    record_id: str,
    ods_code: str,
    message_deduplication_id: str,
    message_group_id: str,
) -> dict[str, Any]:
    return {
        "correlation_id": {"DataType": "String", "StringValue": correlation_id},
        "message_received": {"DataType": "Number", "StringValue": str(message_received)},
        "dynamo_record_id": {"DataType": "String", "StringValue": record_id},
        "ods_code": {"DataType": "String", "StringValue": ods_code},
        "message_deduplication_id": {"DataType": "String", "StringValue": message_deduplication_id},
        "message_group_id": {"DataType": "String", "StringValue": message_group_id},
    }


@patch(f"{FILE_PATH}.review_matches")
@patch(f"{FILE_PATH}.get_matching_services")
@patch(f"{FILE_PATH}.send_update_requests")
@patch(f"{FILE_PATH}.NHSEntity")
@patch(f"{FILE_PATH}.extract_body")
def test_lambda_handler(
    mock_extract_body,
    mock_nhs_entity,
    mock_send_update_requests,
    mock_get_matching_services,
    mock_review_matches,
    change_event,
    lambda_context,
):
    # Arrange
    mock_entity = NHSEntity(change_event)
    sqs_event = SQS_EVENT.copy()
    sqs_event["Records"][0]["body"] = dumps(HOLDING_QUEUE_CHANGE_EVENT_ITEM)
    mock_extract_body.return_value = HOLDING_QUEUE_CHANGE_EVENT_ITEM
    mock_nhs_entity.return_value = mock_entity
    service = dummy_dos_service()
    mock_get_matching_services.return_value = [service]
    mock_review_matches.return_value = [service]
    environ["ENV"] = "test"
    # Act
    response = lambda_handler(sqs_event, lambda_context)
    # Assert
    assert response is None, f"Response should be None but is {response}"
    mock_extract_body.assert_called_once_with(sqs_event["Records"][0]["body"])
    mock_nhs_entity.assert_called_once_with(change_event)
    mock_get_matching_services.assert_called_once_with(mock_entity)
    mock_review_matches.assert_called_once_with([service], mock_entity)
    mock_send_update_requests.assert_called_once_with(
        update_requests=[{"change_event": change_event, "service_id": service.id}],
        message_received=HOLDING_QUEUE_CHANGE_EVENT_ITEM["message_received"],
        record_id=HOLDING_QUEUE_CHANGE_EVENT_ITEM["dynamo_record_id"],
        sequence_number=HOLDING_QUEUE_CHANGE_EVENT_ITEM["sequence_number"],
    )
    # Clean up
    del environ["ENV"]


@patch(f"{FILE_PATH}.get_matching_services")
@patch(f"{FILE_PATH}.send_update_requests")
@patch(f"{FILE_PATH}.NHSEntity")
@patch(f"{FILE_PATH}.extract_body")
def test_lambda_handler_unmatched_service(
    mock_extract_body,
    mock_nhs_entity,
    mock_send_update_requests,
    mock_get_matching_services,
    change_event,
    lambda_context,
):
    # Arrange
    mock_entity = NHSEntity(change_event)
    sqs_event = SQS_EVENT.copy()
    sqs_event["Records"][0]["body"] = dumps(HOLDING_QUEUE_CHANGE_EVENT_ITEM)
    mock_extract_body.return_value = HOLDING_QUEUE_CHANGE_EVENT_ITEM
    mock_nhs_entity.return_value = mock_entity
    mock_get_matching_services.return_value = []
    environ["ENV"] = "test"
    # Act
    response = lambda_handler(sqs_event, lambda_context)
    # Assert
    assert response is None, f"Response should be None but is {response}"
    mock_extract_body.assert_called_once_with(sqs_event["Records"][0]["body"])
    mock_nhs_entity.assert_called_once_with(change_event)
    mock_get_matching_services.assert_called_once_with(mock_entity)
    mock_send_update_requests.assert_not_called()
    # Clean up
    del environ["ENV"]


def test_lambda_handler_should_throw_exception_if_event_records_len_not_eq_one(lambda_context):
    # Arrange
    sqs_event = SQS_EVENT.copy()
    sqs_event["Records"] = []
    environ["ENV"] = "test"
    # Act / Assert
    with pytest.raises(StopIteration):
        lambda_handler(sqs_event, lambda_context)
    # Clean up
    del environ["ENV"]


@patch(f"{FILE_PATH}.sqs")
@patch.object(Logger, "get_correlation_id", return_value="1")
@patch.object(Logger, "warning")
def test_send_update_requests(
    mock_logger,
    get_correlation_id_mock,
    mock_sqs,
) -> None:
    # Arrange
    q_name = "test-queue"
    environ["UPDATE_REQUEST_QUEUE_URL"] = q_name
    message_received = 1642501355616
    record_id = "someid"
    sequence_number = 1
    odscode = "FXXX1"
    update_requests = [{"service_id": "1", "change_event": {"ODSCode": odscode}}]
    # Act
    send_update_requests(
        update_requests=update_requests,
        message_received=message_received,
        record_id=record_id,
        sequence_number=sequence_number,
    )
    # Assert
    payload = dumps(update_requests[0])
    encoded = payload.encode()
    hashed_payload = hashlib.sha256(encoded).hexdigest()
    entry_details = {
        "Id": "1-1",
        "MessageBody": payload,
        "MessageDeduplicationId": f"1-{hashed_payload}",
        "MessageGroupId": "1",
        "MessageAttributes": _get_message_attributes(
            "1",
            message_received,
            record_id,
            odscode,
            f"1-{hashed_payload}",
            "1",
        ),
    }
    mock_sqs.send_message_batch.assert_called_with(
        QueueUrl=q_name,
        Entries=[entry_details],
    )
    mock_logger.assert_called_with(
        "Sent Off Update Request",
        service_id="1",
        environment="local",
        cloudwatch_metric_filter_matching_attribute="UpdateRequestSent",
    )
    # Clean up
    del environ["UPDATE_REQUEST_QUEUE_URL"]


HOLDING_QUEUE_CHANGE_EVENT_ITEM = HoldingQueueChangeEventItem(
    change_event=PHARMACY_STANDARD_EVENT.copy(),
    message_received=1234567890,
    sequence_number=1,
    dynamo_record_id="123",
    correlation_id="correlation_id",
)
SQS_EVENT = {
    "Records": [
        {
            "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
            "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy0a...",
            "body": dumps(HOLDING_QUEUE_CHANGE_EVENT_ITEM),
            "attributes": {
                "ApproximateReceiveCount": "1",
                "SentTimestamp": "1642619743522",
                "SenderId": "AIDAIENQZJOLO23YVJ4VO",
                "ApproximateFirstReceiveTimestamp": "1545082649185",
            },
            "messageAttributes": {
                "correlation-id": {"stringValue": "1", "dataType": "String"},
                "sequence-number": {"stringValue": "1", "dataType": "Number"},
            },
            "md5OfBody": "e4e68fb7bd0e697a0ae8f1bb342846b3",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:my-queue",
            "awsRegion": "us-east-2",
        },
    ],
}
