from json import dumps
from os import environ
from unittest.mock import MagicMock, patch

import pytest
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from application.common.types import HoldingQueueChangeEventItem
from application.conftest import InvocationTracker
from application.ingest_change_event.ingest_change_event import add_change_event_received_metric, lambda_handler

FILE_PATH = "application.ingest_change_event.ingest_change_event"


@patch(f"{FILE_PATH}.sqs")
@patch(f"{FILE_PATH}.HoldingQueueChangeEventItem")
@patch(f"{FILE_PATH}.add_change_event_to_dynamodb")
@patch(f"{FILE_PATH}.get_latest_sequence_id_for_a_given_odscode_from_dynamodb")
@patch(f"{FILE_PATH}.remove_given_keys_from_dict_by_msg_limit")
@patch(f"{FILE_PATH}.get_sequence_number")
@patch(f"{FILE_PATH}.add_change_event_received_metric")
@patch(f"{FILE_PATH}.validate_change_event")
@patch(f"{FILE_PATH}.extract_body")
def test_lambda_handler(
    mock_extract_body: MagicMock,
    mock_validate_change_event: MagicMock,
    mock_add_change_event_received_metric: MagicMock,
    mock_get_sequence_number: MagicMock,
    mock_remove_given_keys_from_dict_by_msg_limit: MagicMock,
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb: MagicMock,
    mock_add_change_event_to_dynamodb: MagicMock,
    mock_holding_queue_change_event_item: MagicMock,
    mock_sqs: MagicMock,
    change_event: dict,
    lambda_context: LambdaContext,
):
    # Arrange
    event = SQS_EVENT.copy()
    event["Records"][0]["body"] = dumps(change_event)
    mock_extract_body.return_value = change_event
    environ["ENV"] = "test"
    environ["HOLDING_QUEUE_URL"] = queue_url = "https://sqs.eu-west-1.amazonaws.com/000000000000/holding-queue"
    sqs_timestamp = 1642619743522
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb.return_value = 1
    mock_get_sequence_number.return_value = sequence_number = 2
    mock_add_change_event_to_dynamodb.return_value = dynamodb_record = "1234567890"
    mock_holding_queue_change_event_item.return_value = holding_queue_change_event_item = HoldingQueueChangeEventItem(
        change_event=None,
        dynamo_record_id=None,
        correlation_id=None,
        sequence_number=None,
        message_received=None,
    )
    # Act
    response = lambda_handler(event, lambda_context)
    # Assert
    assert response is None
    mock_extract_body.assert_called_once_with(dumps(change_event))
    mock_validate_change_event.assert_called_once_with(change_event)
    mock_add_change_event_received_metric.assert_called_once_with(ods_code=change_event["ODSCode"])
    mock_remove_given_keys_from_dict_by_msg_limit.assert_called_once_with(
        change_event,
        ["Facilities", "Metrics"],
        10000,
    )
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb.assert_called_once_with(change_event["ODSCode"])
    mock_add_change_event_to_dynamodb.assert_called_once_with(change_event, sequence_number, sqs_timestamp)
    mock_holding_queue_change_event_item.assert_called_once_with(
        change_event=change_event,
        sequence_number=sequence_number,
        message_received=sqs_timestamp,
        dynamo_record_id=dynamodb_record,
        correlation_id="1",
    )
    mock_sqs.send_message.assert_called_once_with(
        QueueUrl=queue_url,
        MessageBody=dumps(holding_queue_change_event_item),
        MessageGroupId=change_event["ODSCode"],
    )
    # Cleanup
    del environ["ENV"]
    del environ["HOLDING_QUEUE_URL"]


@patch(f"{FILE_PATH}.sqs")
@patch(f"{FILE_PATH}.HoldingQueueChangeEventItem")
@patch(f"{FILE_PATH}.add_change_event_to_dynamodb")
@patch(f"{FILE_PATH}.get_latest_sequence_id_for_a_given_odscode_from_dynamodb")
@patch(f"{FILE_PATH}.remove_given_keys_from_dict_by_msg_limit")
@patch(f"{FILE_PATH}.get_sequence_number")
@patch(f"{FILE_PATH}.add_change_event_received_metric")
@patch(f"{FILE_PATH}.validate_change_event")
def test_lambda_handler_with_sensitive_staff_key(
    mock_validate_change_event: MagicMock,
    mock_add_change_event_received_metric: MagicMock,
    mock_get_sequence_number: MagicMock,
    mock_remove_given_keys_from_dict_by_msg_limit: MagicMock,
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb: MagicMock,
    mock_add_change_event_to_dynamodb: MagicMock,
    mock_holding_queue_change_event_item: MagicMock,
    mock_sqs: MagicMock,
    change_event_staff: dict,
    change_event: dict,
    lambda_context: LambdaContext,
):
    # Arrange
    event = SQS_EVENT.copy()
    event["Records"][0]["body"] = dumps(change_event_staff.copy())
    environ["ENV"] = "test"
    environ["HOLDING_QUEUE_URL"] = queue_url = "https://sqs.eu-west-1.amazonaws.com/000000000000/holding-queue"
    sqs_timestamp = 1642619743522
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb.return_value = 1
    mock_get_sequence_number.return_value = sequence_number = 2
    mock_add_change_event_to_dynamodb.return_value = dynamodb_record = "1234567890"
    mock_holding_queue_change_event_item.return_value = holding_queue_change_event_item = HoldingQueueChangeEventItem(
        change_event=None,
        dynamo_record_id=None,
        correlation_id=None,
        sequence_number=None,
        message_received=None,
    )
    # Act
    response = lambda_handler(event, lambda_context)
    # Assert
    assert response is None
    mock_validate_change_event.assert_called_once_with(change_event)
    mock_add_change_event_received_metric.assert_called_once_with(ods_code=change_event["ODSCode"])
    mock_remove_given_keys_from_dict_by_msg_limit.assert_called_once_with(
        change_event,
        ["Facilities", "Metrics"],
        10000,
    )
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb.assert_called_once_with(change_event["ODSCode"])
    mock_add_change_event_to_dynamodb.assert_called_once_with(change_event, sequence_number, sqs_timestamp)
    mock_holding_queue_change_event_item.assert_called_once_with(
        change_event=change_event,
        sequence_number=sequence_number,
        message_received=sqs_timestamp,
        dynamo_record_id=dynamodb_record,
        correlation_id="1",
    )
    mock_sqs.send_message.assert_called_once_with(
        QueueUrl=queue_url,
        MessageBody=dumps(holding_queue_change_event_item),
        MessageGroupId=change_event["ODSCode"],
    )
    # Cleanup
    del environ["ENV"]
    del environ["HOLDING_QUEUE_URL"]


@patch.object(Logger, "error")
@patch(f"{FILE_PATH}.sqs")
@patch(f"{FILE_PATH}.HoldingQueueChangeEventItem")
@patch(f"{FILE_PATH}.add_change_event_to_dynamodb")
@patch(f"{FILE_PATH}.get_latest_sequence_id_for_a_given_odscode_from_dynamodb")
@patch(f"{FILE_PATH}.remove_given_keys_from_dict_by_msg_limit")
@patch(f"{FILE_PATH}.get_sequence_number")
@patch(f"{FILE_PATH}.add_change_event_received_metric")
@patch(f"{FILE_PATH}.validate_change_event")
@patch(f"{FILE_PATH}.extract_body")
def test_lambda_handler_no_sequence_number(
    mock_extract_body: MagicMock,
    mock_validate_change_event: MagicMock,
    mock_add_change_event_received_metric: MagicMock,
    mock_get_sequence_number: MagicMock,
    mock_remove_given_keys_from_dict_by_msg_limit: MagicMock,
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb: MagicMock,
    mock_add_change_event_to_dynamodb: MagicMock,
    mock_holding_queue_change_event_item: MagicMock,
    mock_sqs: MagicMock,
    mock_logger_error: MagicMock,
    change_event: dict,
    lambda_context: LambdaContext,
):
    # Arrange
    event = SQS_EVENT.copy()
    event["Records"][0]["body"] = dumps(change_event)
    mock_extract_body.return_value = change_event
    environ["ENV"] = "test"
    environ["HOLDING_QUEUE_URL"] = "https://sqs.eu-west-1.amazonaws.com/000000000000/holding-queue"
    sqs_timestamp = 1642619743522
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb.return_value = 1
    mock_get_sequence_number.return_value = sequence_number = None
    mock_add_change_event_to_dynamodb.return_value = "1234567890"
    mock_holding_queue_change_event_item.return_value = HoldingQueueChangeEventItem(
        change_event=None,
        dynamo_record_id=None,
        correlation_id=None,
        sequence_number=None,
        message_received=None,
    )
    # Act
    response = lambda_handler(event, lambda_context)
    # Assert
    assert response is None
    mock_extract_body.assert_called_once_with(dumps(change_event))
    mock_validate_change_event.assert_called_once_with(change_event)
    mock_add_change_event_received_metric.assert_called_once_with(ods_code=change_event["ODSCode"])
    mock_remove_given_keys_from_dict_by_msg_limit.assert_called_once_with(
        change_event,
        ["Facilities", "Metrics"],
        10000,
    )
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb.assert_called_once_with(change_event["ODSCode"])
    mock_add_change_event_to_dynamodb.assert_called_once_with(change_event, sequence_number, sqs_timestamp)
    mock_holding_queue_change_event_item.assert_not_called()
    mock_sqs.send_message.assert_not_called()
    mock_logger_error.assert_called_once_with("No sequence number provided, so message will be ignored.")
    # Cleanup
    del environ["ENV"]
    del environ["HOLDING_QUEUE_URL"]


@patch.object(Logger, "error")
@patch(f"{FILE_PATH}.sqs")
@patch(f"{FILE_PATH}.HoldingQueueChangeEventItem")
@patch(f"{FILE_PATH}.add_change_event_to_dynamodb")
@patch(f"{FILE_PATH}.get_latest_sequence_id_for_a_given_odscode_from_dynamodb")
@patch(f"{FILE_PATH}.remove_given_keys_from_dict_by_msg_limit")
@patch(f"{FILE_PATH}.get_sequence_number")
@patch(f"{FILE_PATH}.add_change_event_received_metric")
@patch(f"{FILE_PATH}.validate_change_event")
@patch(f"{FILE_PATH}.extract_body")
def test_lambda_handler_less_than_latest_sequence_number(
    mock_extract_body: MagicMock,
    mock_validate_change_event: MagicMock,
    mock_add_change_event_received_metric: MagicMock,
    mock_get_sequence_number: MagicMock,
    mock_remove_given_keys_from_dict_by_msg_limit: MagicMock,
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb: MagicMock,
    mock_add_change_event_to_dynamodb: MagicMock,
    mock_holding_queue_change_event_item: MagicMock,
    mock_sqs: MagicMock,
    mock_logger_error: MagicMock,
    change_event: dict,
    lambda_context: LambdaContext,
):
    # Arrange
    event = SQS_EVENT.copy()
    event["Records"][0]["body"] = dumps(change_event)
    mock_extract_body.return_value = change_event
    environ["ENV"] = "test"
    environ["HOLDING_QUEUE_URL"] = "https://sqs.eu-west-1.amazonaws.com/000000000000/holding-queue"
    sqs_timestamp = 1642619743522
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb.return_value = db_latest_sequence_number = 2
    mock_get_sequence_number.return_value = sequence_number = 1
    mock_add_change_event_to_dynamodb.return_value = "1234567890"
    mock_holding_queue_change_event_item.return_value = HoldingQueueChangeEventItem(
        change_event=None,
        dynamo_record_id=None,
        correlation_id=None,
        sequence_number=None,
        message_received=None,
    )
    # Act
    response = lambda_handler(event, lambda_context)
    # Assert
    assert response is None
    mock_extract_body.assert_called_once_with(dumps(change_event))
    mock_validate_change_event.assert_called_once_with(change_event)
    mock_add_change_event_received_metric.assert_called_once_with(ods_code=change_event["ODSCode"])
    mock_remove_given_keys_from_dict_by_msg_limit.assert_called_once_with(
        change_event,
        ["Facilities", "Metrics"],
        10000,
    )
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb.assert_called_once_with(change_event["ODSCode"])
    mock_add_change_event_to_dynamodb.assert_called_once_with(change_event, sequence_number, sqs_timestamp)
    mock_holding_queue_change_event_item.assert_not_called()
    mock_sqs.send_message.assert_not_called()
    mock_logger_error.assert_called_once_with(
        "Sequence id is smaller than the existing one in db for a given odscode, so will be ignored",
        incoming_sequence_number=sequence_number,
        db_latest_sequence_number=db_latest_sequence_number,
    )
    # Cleanup
    del environ["ENV"]
    del environ["HOLDING_QUEUE_URL"]


@patch(f"{FILE_PATH}.sqs")
@patch(f"{FILE_PATH}.HoldingQueueChangeEventItem")
@patch(f"{FILE_PATH}.add_change_event_to_dynamodb")
@patch(f"{FILE_PATH}.get_latest_sequence_id_for_a_given_odscode_from_dynamodb")
@patch(f"{FILE_PATH}.remove_given_keys_from_dict_by_msg_limit")
@patch(f"{FILE_PATH}.get_sequence_number")
@patch(f"{FILE_PATH}.add_change_event_received_metric")
@patch(f"{FILE_PATH}.validate_change_event")
@patch(f"{FILE_PATH}.extract_body")
def test_lambda_handler_mutiple_records(
    mock_extract_body: MagicMock,
    mock_validate_change_event: MagicMock,
    mock_add_change_event_received_metric: MagicMock,
    mock_get_sequence_number: MagicMock,
    mock_remove_given_keys_from_dict_by_msg_limit: MagicMock,
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb: MagicMock,
    mock_add_change_event_to_dynamodb: MagicMock,
    mock_holding_queue_change_event_item: MagicMock,
    mock_sqs: MagicMock,
    change_event: dict,
    lambda_context: LambdaContext,
):
    # Arrange
    event = SQS_EVENT.copy()
    record = event["Records"][0]
    records_list = [record, record, record]
    event["Records"] = records_list
    mock_extract_body.return_value = change_event
    environ["ENV"] = "test"
    environ["HOLDING_QUEUE_URL"] = "https://sqs.eu-west-1.amazonaws.com/000000000000/holding-queue"
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb.return_value = 2
    mock_get_sequence_number.return_value = 1
    mock_add_change_event_to_dynamodb.return_value = "1234567890"
    mock_holding_queue_change_event_item.return_value = HoldingQueueChangeEventItem(
        change_event=None,
        dynamo_record_id=None,
        correlation_id=None,
        sequence_number=None,
        message_received=None,
    )
    # Act
    with pytest.raises(ValueError, match="3 records found in event. Expected 1."):
        lambda_handler(event, lambda_context)
    # Assert
    mock_extract_body.assert_not_called()
    mock_validate_change_event.assert_not_called()
    mock_add_change_event_received_metric.assert_not_called()
    mock_remove_given_keys_from_dict_by_msg_limit.assert_not_called()
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb.assert_not_called()
    mock_add_change_event_to_dynamodb.assert_not_called()
    mock_holding_queue_change_event_item.assert_not_called()
    mock_sqs.send_message.assert_not_called()
    # Cleanup
    del environ["ENV"]
    del environ["HOLDING_QUEUE_URL"]


def test_add_change_event_received_metric():
    # Arrange
    odscode = "V12345"
    environ["ENV"] = "test"
    # Act
    add_change_event_received_metric(odscode)
    # Assert
    assert InvocationTracker.invocations == 1
    # Cleanup
    InvocationTracker.reset()
    del environ["ENV"]


SQS_EVENT = {
    "Records": [
        {
            "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
            "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy0a...",
            "body": "Test message.",
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
