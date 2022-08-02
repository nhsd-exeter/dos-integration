from dataclasses import dataclass
from json import dumps
from os import environ
from unittest.mock import Mock, patch

from pytest import approx, fixture

from application.orchestrator.orchestrator import invoke_lambda, lambda_handler

from common.types import UpdateRequestMetadata, UpdateRequestQueueItem

FILE_PATH = "application.orchestrator.orchestrator"


@fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = "dos-db-update-dlq-handler"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:dos-db-update-dlq-handler"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()


LAMBDA_INVOKE_RESPONSE = {
    "Payload": "",
    "StatusCode": 202,
    "ResponseMetadata": {},
}


def test_invoke_lambda(lambda_context):
    # Arrange
    client_mock = Mock()
    environ["EVENT_SENDER_FUNCTION_NAME"] = "MyFirstFunction"
    expected = LAMBDA_INVOKE_RESPONSE
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


EXAMPLE_ATTRIBUTES = {
    "correlation_id": {"StringValue": "c1"},
    "dynamo_record_id": {"StringValue": "d1"},
    "message_received": {"StringValue": "1645527100000"},
    "ods_code": {"StringValue": "FA100"},
    "message_deduplication_id": {"StringValue": "dummy_message_deduplication_id"},
    "message_group_id": {"StringValue": "dummy_message_group_id"},
}

EXPECTED_METADATA: UpdateRequestMetadata = {
    "dynamo_record_id": "d1",
    "correlation_id": "c1",
    "message_received": "1645527100000",
    "ods_code": "FA100",
}
SYSTEM = "DoS Integration"
MESSAGE = "Some message"
EXAMPLE_MESSAGE_1 = {
    "reference": "",
    "system": SYSTEM,
    "message": MESSAGE,
    "service_id": "100",
    "changes": [],
}
EXAMPLE_MESSAGE_2 = {
    "reference": "",
    "system": SYSTEM,
    "message": MESSAGE,
    "service_id": "200",
    "changes": [],
}

EXAMPLE_MESSAGE_3 = {
    "reference": "",
    "system": SYSTEM,
    "message": MESSAGE,
    "service_id": "300",
    "changes": [],
}

EXPECTED_HEALTH_CHECK: UpdateRequestQueueItem = {
    "is_health_check": True,
    "update_request": None,
    "recipient_id": None,
    "metadata": None,
}


@patch(f"{FILE_PATH}.get_circuit_is_open", return_value=False)
@patch(f"{FILE_PATH}.client")
@patch(f"{FILE_PATH}.invoke_lambda")
@patch(f"{FILE_PATH}.sleep")
@patch(
    f"{FILE_PATH}.time",
    side_effect=[1645527500, 1645527501, 1645527501, 1645527501.1, 1645527501.5, 1645527501.7, 1645527511],
)
def test_orchestrator_circuit_closed_single_loop(mock_time, mock_sleep, mock_invoke, mock_client, lambda_context):

    # Arrange
    environ["RUN_FOR"] = "10"
    environ["CIRCUIT"] = "TEST"
    environ["SLEEP_FOR_WHEN_OPEN"] = "5"
    environ["DOS_TRANSACTIONS_PER_SECOND"] = "2"
    mock_invoke.return_value = LAMBDA_INVOKE_RESPONSE
    mock_client().invoke.return_value = {}
    mock_client().receive_message.return_value = {
        "Messages": [
            {"MessageAttributes": EXAMPLE_ATTRIBUTES, "Body": dumps(EXAMPLE_MESSAGE_1), "ReceiptHandle": "H1"},
            {"MessageAttributes": EXAMPLE_ATTRIBUTES, "Body": dumps(EXAMPLE_MESSAGE_2), "ReceiptHandle": "H2"},
        ]
    }

    # Act
    lambda_handler({}, lambda_context)

    # Assert
    assert 2 == mock_invoke.call_count
    assert 2 == mock_sleep.call_count

    c0_args, c0_kwargs = mock_sleep.call_args_list[0]
    c1_args, c1_kwargs = mock_sleep.call_args_list[1]
    assert 0.4 == approx(c0_args[0])
    assert 0.3 == approx(c1_args[0])


@patch(f"{FILE_PATH}.get_circuit_is_open", return_value=False)
@patch(f"{FILE_PATH}.client")
@patch(f"{FILE_PATH}.invoke_lambda")
@patch(f"{FILE_PATH}.sleep")
@patch(
    f"{FILE_PATH}.time",
    side_effect=[
        1645527500,
        1645527501,
        1645527501,
        1645527501.1,
        1645527501.5,
        1645527501.7,
        1645527506,
        1645527506,
        1645527506.7,
        1645527511,
    ],
)
def test_orchestrator_circuit_closed_double_loop(mock_time, mock_sleep, mock_invoke, mock_client, lambda_context):

    # Arrange
    environ["RUN_FOR"] = "10"
    environ["CIRCUIT"] = "TEST"
    environ["SLEEP_FOR_WHEN_OPEN"] = "5"
    environ["DOS_TRANSACTIONS_PER_SECOND"] = "2"
    mock_invoke.return_value = LAMBDA_INVOKE_RESPONSE
    mock_client().invoke.return_value = {}
    mock_client().receive_message.side_effect = [
        {
            "Messages": [
                {"MessageAttributes": EXAMPLE_ATTRIBUTES, "Body": dumps(EXAMPLE_MESSAGE_1), "ReceiptHandle": "H1"},
                {"MessageAttributes": EXAMPLE_ATTRIBUTES, "Body": dumps(EXAMPLE_MESSAGE_2), "ReceiptHandle": "H2"},
            ]
        },
        {
            "Messages": [
                {"MessageAttributes": EXAMPLE_ATTRIBUTES, "Body": dumps(EXAMPLE_MESSAGE_3), "ReceiptHandle": "H3"},
            ]
        },
    ]

    # Act
    lambda_handler({}, lambda_context)

    # Assert
    assert 3 == mock_invoke.call_count
    assert 3 == mock_sleep.call_count

    c0_args, c0_kwargs = mock_sleep.call_args_list[0]
    c1_args, c1_kwargs = mock_sleep.call_args_list[1]
    c2_args, c2_kwargs = mock_sleep.call_args_list[2]
    assert 0.4 == approx(c0_args[0])
    assert 0.3 == approx(c1_args[0])
    assert 0 == approx(c2_args[0])


@patch(f"{FILE_PATH}.get_circuit_is_open", return_value=False)
@patch(f"{FILE_PATH}.client")
@patch(f"{FILE_PATH}.invoke_lambda")
@patch(f"{FILE_PATH}.sleep")
@patch(f"{FILE_PATH}.time", side_effect=[1645527500, 1645527501, 1645527511])
def test_orchestrator_circuit_closed_single_loop_no_messages(
    mock_time, mock_sleep, mock_invoke, mock_client, lambda_context
):
    # Arrange
    environ["RUN_FOR"] = "10"
    environ["CIRCUIT"] = "TEST"
    environ["SLEEP_FOR_WHEN_OPEN"] = "5"
    environ["DOS_TRANSACTIONS_PER_SECOND"] = "2"
    mock_invoke.return_value = LAMBDA_INVOKE_RESPONSE
    mock_client().invoke.return_value = {}
    mock_client().receive_message.return_value = {}

    # Act
    lambda_handler({}, lambda_context)

    # Assert
    assert 3 == mock_time.call_count
    assert 0 == mock_invoke.call_count
    assert 1 == mock_sleep.call_count

    mock_sleep.assert_called_once_with(1)


@patch(f"{FILE_PATH}.get_circuit_is_open", return_value=True)
@patch(f"{FILE_PATH}.client")
@patch(f"{FILE_PATH}.invoke_lambda")
@patch(f"{FILE_PATH}.sleep")
@patch(f"{FILE_PATH}.time", side_effect=[1645527500, 1645527501, 1645527511])
def test_orchestrator_circuit_closed_single_loop_circuit_open(
    mock_time, mock_sleep, mock_invoke, mock_client, lambda_context
):
    # Arrange
    environ["RUN_FOR"] = "10"
    environ["CIRCUIT"] = "TEST"
    environ["SLEEP_FOR_WHEN_OPEN"] = "5"
    environ["DOS_TRANSACTIONS_PER_SECOND"] = "2"
    mock_invoke.return_value = LAMBDA_INVOKE_RESPONSE
    mock_client().invoke.return_value = {}
    mock_client().receive_message.return_value = {}

    # Act
    lambda_handler({}, lambda_context)

    # Assert
    assert 3 == mock_time.call_count
    assert 1 == mock_invoke.call_count
    assert 1 == mock_sleep.call_count
    mock_invoke.assert_called_once_with(mock_client(), EXPECTED_HEALTH_CHECK)

    mock_sleep.assert_called_once_with(5)
