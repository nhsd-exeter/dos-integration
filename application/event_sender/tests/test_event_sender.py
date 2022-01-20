from unittest.mock import patch
from dataclasses import dataclass
from os import environ
from aws_embedded_metrics.logger.metrics_logger import MetricsLogger
import pytest
import json
from ..event_sender import lambda_handler

CHANGE_REQUEST = {
    "reference": "1",
    "system": "Profile Updater (test)",
    "message": "Test message 1531816592293|@./",
    "service_id": "49016",
    "changes": {"ods_code": "f0000", "phone": "0118 999 88199 9119 725 3", "website": "https://www.google.pl"},
}
BODY = json.dumps(
    {
        "change_payload": CHANGE_REQUEST,
        "correlation_id": "dummy_correlation_id",
        "message_received": 1642619743522,
        "ods_code": "FX100",
        "dynamo_record_id": "EXAMPLE",
    }
)
EVENT = {"body": BODY}

FILE_PATH = "application.event_sender.event_sender"


@pytest.fixture
def mock_logger():
    InvocationTracker.reset()

    async def flush(self):
        print("flush called")
        InvocationTracker.record()

    MetricsLogger.flush = flush


@pytest.fixture
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

@patch(f"{FILE_PATH}.ChangeRequest")
@patch(f"{FILE_PATH}.time_ns", return_value=1642619746522500523)
@patch.object(MetricsLogger,'put_metric')
@patch.object(MetricsLogger,'put_dimensions')
def test_lambda_handler_dos_api_success(mock_put_dimension, mock_put_metric,mock_time, mock_change_request, lambda_context, mock_logger):

    mock_instance = mock_change_request.return_value
    mock_instance.post_change_request.return_value = MockResponse(status_code=200,text="success")
    environ["ENV"] = "test"
    environ["DOS_API_GATEWAY_REQUEST_TIMEOUT"] = "1"

    # Act
    response = lambda_handler(EVENT, lambda_context)
    # Assert

    mock_change_request.assert_called_once_with(CHANGE_REQUEST)
    mock_instance.post_change_request.assert_called_once_with()
    mock_put_dimension.assert_called_once_with({"ENV":"test"})
    mock_put_metric.assert_called_once_with("ProcessingLatency", 3000, "Milliseconds")
    assert response["statusCode"] == 200
    assert response["body"] == "success"

@patch(f"{FILE_PATH}.ChangeRequest")
@patch.object(MetricsLogger,'put_metric')
@patch.object(MetricsLogger,'put_dimensions')
def test_lambda_handler_dos_api_fail(mock_put_dimension, mock_put_metric, mock_change_request, lambda_context, mock_logger):


    mock_instance = mock_change_request.return_value
    mock_instance.post_change_request.return_value = MockResponse(status_code=500,text="something went wrong")

    environ["ENV"] = "test"
    # Act
    response = lambda_handler(EVENT, lambda_context)
    # Assert

    mock_change_request.assert_called_once_with(CHANGE_REQUEST)
    mock_change_request().post_change_request.assert_called_once_with()
    mock_put_dimension.assert_called_once_with({"ENV":"test"})
    mock_put_metric.assert_called_once_with("DoSApiFail", 1, "Count")
    assert response["statusCode"] == 500
    assert response["body"] == "something went wrong"


class InvocationTracker(object):
    invocations = 0

    @staticmethod
    def record():
        InvocationTracker.invocations += 1

    @staticmethod
    def reset():
        InvocationTracker.invocations = 0
