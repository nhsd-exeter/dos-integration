from unittest.mock import MagicMock

from application.common.types import UpdateRequest, UpdateRequestMetadata, UpdateRequestQueueItem


def test_update_request():
    # Arrange
    change_event = {"ODSCode": "12345"}
    service_id = "1"
    # Act
    response = UpdateRequest(change_event=change_event, service_id=service_id)
    # Assert
    assert change_event == response["change_event"]
    assert service_id == response["service_id"]


def test_update_request_metadata():
    # Arrange
    dynamo_record_id = "dynamo_record_id"
    correlation_id = "correlation_id"
    message_received = 1
    ods_code = "ods_code"
    message_deduplication_id = "message_deduplication_id"
    message_group_id = "message_group_id"
    # Act
    response = UpdateRequestMetadata(
        dynamo_record_id=dynamo_record_id,
        correlation_id=correlation_id,
        message_received=message_received,
        ods_code=ods_code,
        message_deduplication_id=message_deduplication_id,
        message_group_id=message_group_id,
    )
    # Assert
    assert dynamo_record_id == response["dynamo_record_id"]
    assert correlation_id == response["correlation_id"]
    assert message_received == response["message_received"]
    assert ods_code == response["ods_code"]
    assert message_deduplication_id == response["message_deduplication_id"]
    assert message_group_id == response["message_group_id"]


def test_update_request_queue_item():
    # Arrange
    update_request = MagicMock()
    recipient_id = "recipient_id"
    metadata = MagicMock()
    # Act
    response = UpdateRequestQueueItem(update_request=update_request, recipient_id=recipient_id, metadata=metadata)
    # Assert
    assert update_request == response["update_request"]
    assert recipient_id == response["recipient_id"]
    assert metadata == response["metadata"]
