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
    {"change_payload": CHANGE_REQUEST, "correlation_id": "dummy_correlation_id", "message_received": 1642501355616}
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


@patch(f"{FILE_PATH}.ChangeRequest")
def test_lambda_handler(mock_change_request, lambda_context, mock_logger):

    environ["ENV"] = "test"
    # Act
    lambda_handler(EVENT, lambda_context)
    # Assert
    mock_change_request.assert_called_once_with(CHANGE_REQUEST)
    mock_change_request().post_change_request.assert_called_once_with()


class InvocationTracker(object):
    invocations = 0

    @staticmethod
    def record():
        InvocationTracker.invocations += 1

    @staticmethod
    def reset():
        InvocationTracker.invocations = 0
