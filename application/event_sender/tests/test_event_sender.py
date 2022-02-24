from dataclasses import dataclass
from json import dumps
from os import environ
from unittest.mock import call, patch

from aws_embedded_metrics.logger.metrics_logger import MetricsLogger
from pytest import fixture

from application.common.types import ChangeMetadata, ChangeRequestQueueItem

from ..event_sender import lambda_handler

CHANGE_REQUEST = {
    "reference": "1",
    "system": "Profile Updater (test)",
    "message": "Test message 1531816592293|@./",
    "service_id": "49016",
    "changes": {"ods_code": "f0000", "phone": "0118 999 88199 9119 725 3", "website": "https://www.google.pl"},
}
METADATA: ChangeMetadata = {
    "dynamo_record_id": "EXAMPLE",
    "correlation_id": "dummy_correlation_id",
    "message_received": 1642619743522,
    "ods_code": "FX100",
    "message_deduplication_id": "dummy_message_deduplication_id",
    "message_group_id": "dummy_message_group_id",
}

EVENT: ChangeRequestQueueItem = {
    "change_request": CHANGE_REQUEST,
    "recipient_id": "r-1",
    "metadata": METADATA,
    "is_health_check": False,
}

FILE_PATH = "application.event_sender.event_sender"


@fixture
def mock_logger():
    InvocationTracker.reset()

    async def flush(self):
        print("flush called")
        InvocationTracker.record()

    MetricsLogger.flush = flush


@fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = "event-sender"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:event-sender"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()


class MockResponse:
    def __init__(self, status_code, text=""):
        self.status_code = status_code
        self.text = text

    @property
    def ok(self):
        return self.status_code < 400


@patch(f"{FILE_PATH}.ChangeRequest")
@patch(f"{FILE_PATH}.time_ns", return_value=1642619746522500523)
@patch.object(MetricsLogger, "put_metric")
@patch.object(MetricsLogger, "set_dimensions")
@patch(f"{FILE_PATH}.client")
def test_lambda_handler_dos_api_success(
    mock_client, mock_set_dimension, mock_put_metric, mock_time, mock_change_request, lambda_context, mock_logger
):
    # Arrange
    environ["CR_QUEUE_URL"] = "test_q"
    environ["CIRCUIT"] = "testcircuit"
    mock_instance = mock_change_request.return_value
    mock_instance.post_change_request.return_value = MockResponse(status_code=201, text="success")
    environ["ENV"] = "test"
    environ["DOS_API_GATEWAY_REQUEST_TIMEOUT"] = "1"
    # Act
    response = lambda_handler(EVENT, lambda_context)
    # Assert
    assert response["statusCode"] == 201
    assert response["body"] == "success"
    mock_client.assert_called_with("sqs")
    mock_change_request.assert_called_once_with(CHANGE_REQUEST)
    mock_instance.post_change_request.assert_called_once_with()
    mock_set_dimension.assert_called_once_with({"ENV": "test"})

    mock_put_metric.assert_has_calls(
        [call("DosApiLatency", 0, "Milliseconds"), call("QueueToDoSLatency", 3000, "Milliseconds")]
    )
    mock_client.return_value.delete_message.assert_called_with(
        QueueUrl="test_q",
        ReceiptHandle="r-1",
    )
    # Cleanup
    del environ["CR_QUEUE_URL"]
    del environ["CIRCUIT"]


@patch(f"{FILE_PATH}.ChangeRequest")
@patch(f"{FILE_PATH}.time_ns", return_value=1642619746522500523)
@patch(f"{FILE_PATH}.put_circuit_is_open")
@patch.object(MetricsLogger, "put_metric")
@patch.object(MetricsLogger, "set_dimensions")
@patch(f"{FILE_PATH}.client")
def test_lambda_handler_dos_api_fail(
    mock_client,
    mock_set_dimension,
    mock_put_metric,
    put_circuit_mock,
    mock_time,
    mock_change_request,
    lambda_context,
    mock_logger,
):
    # Arrange
    mock_instance = mock_change_request.return_value
    mock_instance.post_change_request.return_value = MockResponse(status_code=500, text="something went wrong")
    environ["ENV"] = "test"
    environ["CIRCUIT"] = "testcircuit"
    # Act
    response = lambda_handler(EVENT, lambda_context)
    # Assert
    assert response["statusCode"] == 201
    assert response["body"] == "success"
    mock_client.assert_called_with("sqs")
    mock_change_request.assert_called_once_with(CHANGE_REQUEST)
    mock_change_request().post_change_request.assert_called_once_with()
    mock_set_dimension.assert_called_once_with({"ENV": "test"})
    mock_put_metric.assert_has_calls([call("DosApiLatency", 0, "Milliseconds"), call("DoSApiFail", 1, "Count")])
    mock_client.return_value.delete_message.assert_not_called()
    put_circuit_mock.assert_called_once_with("testcircuit", True)
    # Clean up
    del environ["CIRCUIT"]


@patch(f"{FILE_PATH}.ChangeRequest")
@patch(f"{FILE_PATH}.time_ns", return_value=1642619746522500523)
@patch(f"{FILE_PATH}.put_circuit_is_open")
@patch.object(MetricsLogger, "put_metric")
@patch(f"{FILE_PATH}.client")
def test_lambda_handler_health_check(
    mock_client, mock_put_metric, put_circuit_mock, mock_time, mock_change_request, lambda_context, mock_logger
):
    # Arrange
    environ["CR_QUEUE_URL"] = "test_q"
    environ["CIRCUIT"] = "testcircuit"
    mock_instance = mock_change_request.return_value
    mock_instance.post_change_request.return_value = MockResponse(status_code=400, text="Bad request")
    environ["ENV"] = "test"
    environ["DOS_API_GATEWAY_REQUEST_TIMEOUT"] = "1"
    HEALTH_EVENT = EVENT.copy()
    HEALTH_EVENT["is_health_check"] = True
    # Act
    response = lambda_handler(EVENT, lambda_context)
    # Assert
    assert response["statusCode"] == 201
    assert response["body"] == "success"
    mock_client.assert_called_with("sqs")
    mock_instance.post_change_request.assert_called_once()
    mock_put_metric.assert_not_called()
    put_circuit_mock.assert_called_once_with("testcircuit", False)
    # Clean up
    del environ["CR_QUEUE_URL"]
    del environ["CIRCUIT"]


@patch(f"{FILE_PATH}.ChangeRequest")
@patch(f"{FILE_PATH}.time_ns", return_value=1642619746522500523)
@patch(f"{FILE_PATH}.put_circuit_is_open")
@patch.object(MetricsLogger, "put_metric")
@patch.object(MetricsLogger, "set_dimensions")
@patch(f"{FILE_PATH}.client")
def test_lambda_handler_non_recoverable_error(
    mock_client,
    mock_set_dimension,
    mock_put_metric,
    put_circuit_mock,
    mock_time,
    mock_change_request,
    lambda_context,
    mock_logger,
):
    # Arrange
    error_message = "My error"
    status_code = 400
    dlq_queue_name = "dlq-queue"
    incoming_queue_url = "https://sqs.us-east-1.amazonaws.com/123456789012/incoming-queue"
    mock_instance = mock_change_request.return_value
    mock_instance.post_change_request.return_value = MockResponse(status_code=status_code, text=error_message)

    environ["ENV"] = "test"
    environ["CIRCUIT"] = "testcircuit"
    environ["CR_DLQ_URL"] = dlq_queue_name
    environ["CR_QUEUE_URL"] = incoming_queue_url
    # Act
    response = lambda_handler(EVENT, lambda_context)
    # Assert
    assert response["statusCode"] == 201
    assert response["body"] == "success"
    mock_client.assert_called_with("sqs")
    mock_change_request.assert_called_once_with(CHANGE_REQUEST)
    mock_change_request().post_change_request.assert_called_once_with()
    mock_set_dimension.assert_called_once_with({"ENV": "test"})
    mock_put_metric.assert_has_calls([call("DosApiLatency", 0, "Milliseconds"), call("DoSApiFail", 1, "Count")])
    mock_client().send_message.assert_called_once_with(
        QueueUrl=dlq_queue_name,
        MessageBody=dumps(EVENT["change_request"]),
        MessageDeduplicationId=METADATA["message_deduplication_id"],
        MessageGroupId=METADATA["message_group_id"],
        MessageAttributes={
            "correlation_id": {"DataType": "String", "StringValue": METADATA["correlation_id"]},
            "message_received": {"DataType": "Number", "StringValue": str(METADATA["message_received"])},
            "dynamo_record_id": {"DataType": "String", "StringValue": METADATA["dynamo_record_id"]},
            "ods_code": {"DataType": "String", "StringValue": METADATA["ods_code"]},
            "error_msg": {"DataType": "String", "StringValue": error_message},
            "error_msg_http_code": {"DataType": "String", "StringValue": str(status_code)},
        },
    )
    mock_client().delete_message.assert_called_once_with(
        QueueUrl=incoming_queue_url, ReceiptHandle=EVENT["recipient_id"]
    )
    put_circuit_mock.assert_not_called()
    # Clean up
    environment_variables = ["CIRCUIT", "CR_DLQ_URL", "CR_QUEUE_URL", "ENV"]
    for variable in environment_variables:
        del environ[variable]


class InvocationTracker(object):
    invocations = 0

    @staticmethod
    def record():
        InvocationTracker.invocations += 1

    @staticmethod
    def reset():
        InvocationTracker.invocations = 0
