from json import dumps
from os import environ
from application.orchestrator.orchestrator import invoke_lambda

from unittest.mock import Mock

FILE_PATH = "application.orchestrator.orchestrator"


def test_invoke_lambda():
    # Arrange
    client_mock = Mock()
    environ["EVENT_SENDER_FUNCTION_NAME"] = "MyFirstFunction"
    expected = {
        "Payload": "",
        "StatusCode": 202,
        "ResponseMetadata": {},
    }
    client_mock.invoke.return_value = expected

    # Act
    payload = {"hello": "dave"}
    response = invoke_lambda(client_mock, payload)
    # Assert
    client_mock.invoke.assert_called_once_with(
        FunctionName="MyFirstFunction", InvocationType="Event", Payload=dumps(payload)
    )
    assert response == expected
    del environ["EVENT_SENDER_FUNCTION_NAME"]
