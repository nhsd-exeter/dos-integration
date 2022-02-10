from json import dumps
from typing import Any, Dict
from unittest.mock import patch

from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from pytest import fixture

from application.event_replay.event_replay import lambda_handler

FILE_PATH = "application.event_replay.event_replay"


@fixture
def event() -> Dict[str, Any]:
    return {
        "odscode": "ODS_CODE",
        "sequence_number": "SEQUENCE_NUMBER",
    }


@patch(f"{FILE_PATH}.build_correlation_id")
def test_lambda_handler(mock_build_correlation_id):
    # Arrange
    context = LambdaContext()
    correlation_id = "CORRELATION_ID"
    mock_build_correlation_id.return_value = correlation_id
    # Act
    response = lambda_handler(event, context)
    # Assert
    assert response == dumps({"message": "OK", "correlation_id": correlation_id})


def test_validate_event():
    pass


def test_build_correlation_id():
    pass


def test_get_change_event():
    pass


def test_send_change_event():
    pass
