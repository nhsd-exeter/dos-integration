from unittest.mock import MagicMock, Mock, patch
from pytest import fixture
from dataclasses import dataclass
from os import environ
from json import dumps
from common.encryption import validate_signing_key, validate_event_is_signed, initialise_encryption_client, BAD_REQUEST
from aws_encryption_sdk.exceptions import SerializationError


@fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = "event-processor"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:event-processor"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()


@patch("common.encryption.initialise_encryption_client")
def test_validate_signing_not_base64(mock_client):
    # Arrange
    mock_e = Mock()
    mock_e.encrypt_string = lambda a: "encrypted"
    mock_e.decrypt_string = lambda a: "decrypted"
    mock_client.return_value = mock_e
    # Act
    response = validate_signing_key("Hello dave", {})
    # Assert
    assert response is False


def mock_decrypt():
    raise SerializationError()


@patch("common.encryption.initialise_encryption_client")
def test_validate_signing_valid_base64_invalid_sig(mock_client):
    # Arrange
    mock_e = Mock()
    mock_e.encrypt_string = lambda a: "encrypted"
    mock_e.decrypt_string = mock_decrypt
    mock_client.return_value = mock_e
    # Act
    response = validate_signing_key("aGVsbG8=", "{}")
    # Assert
    assert response is False


@patch("common.encryption.initialise_encryption_client")
def test_validate_signing_valid_no_ods_match(mock_client):
    # Arrange
    expected_response = {
        "ods_code": "A",
    }
    mock_e = Mock()
    mock_e.encrypt_string = lambda a: "encrypted"
    mock_e.decrypt_string = lambda a: dumps(expected_response)
    mock_client.return_value = mock_e
    # Act
    response = validate_signing_key("aGVsbG8=", {"ods_code": "B"})
    # Assert
    assert response is False


@patch("common.encryption.initialise_encryption_client")
@patch("common.encryption.time", return_value=1643186744.55731)
def test_validate_signing_valid(mock_time, mock_client):
    # Arrange
    expected_response = {"ods_code": "A", "dynamo_record_id": "1", "message_received": 1, "time": 1643186734.55731}
    mock_e = Mock()
    mock_e.encrypt_string = lambda a: "encrypted"
    mock_e.decrypt_string = lambda a: dumps(expected_response)
    mock_client.return_value = mock_e
    # Act
    response = validate_signing_key(
        "aGVsbG8=",
        {
            "ods_code": "A",
            "dynamo_record_id": "1",
            "message_received": 1,
        },
    )
    # Assert
    assert response is True


@patch("common.encryption.initialise_encryption_client")
@patch("common.encryption.time", return_value=1643186744.55731)
def test_validate_signing_valid_timed_out(mock_time, mock_client):
    # Arrange
    expected_response = {"ods_code": "A", "dynamo_record_id": "1", "message_received": 1, "time": 1643086744.55731}
    mock_e = Mock()
    mock_e.encrypt_string = lambda a: "encrypted"
    mock_e.decrypt_string = lambda a: dumps(expected_response)
    mock_client.return_value = mock_e

    # Act
    response = validate_signing_key(
        "aGVsbG8=",
        {
            "ods_code": "A",
            "dynamo_record_id": "1",
            "message_received": 1,
        },
    )
    # Assert
    assert response is False


@patch("common.encryption.validate_signing_key", return_value=True)
def test_validation_decorator(mock_client, lambda_context):
    # Arrange
    mock_handler = MagicMock()
    mock_handler.return_value = "Dave"
    mock_body = {"signing_key": "hello"}
    # Act
    response = validate_event_is_signed.__wrapped__(mock_handler, {"body": dumps(mock_body)}, lambda_context)
    # Assert
    mock_handler.assert_called_once()
    assert response == "Dave"


@patch("common.encryption.validate_signing_key", return_value=True)
def test_validation_decorator_no_signing_key(mock_client, lambda_context):
    # Arrange
    mock_handler = MagicMock()

    mock_body = {}
    # Act
    response = validate_event_is_signed.__wrapped__(mock_handler, {"body": dumps(mock_body)}, lambda_context)
    # Assert
    mock_handler.assert_not_called()
    assert response == BAD_REQUEST


@patch("common.encryption.validate_signing_key", return_value=False)
def test_validation_decorator_invalid_key(mock_client, lambda_context):
    # Arrange
    mock_handler = MagicMock()
    mock_body = {}
    # Act
    response = validate_event_is_signed.__wrapped__(mock_handler, {"body": dumps(mock_body)}, lambda_context)
    # Assert
    mock_handler.assert_not_called()
    assert response == BAD_REQUEST


@patch("common.encryption_helper.StrictAwsKmsMasterKeyProvider")
@patch("common.encryption_helper.EncryptionSDKClient")
@patch("common.encryption_helper.client")
def test_initalise_encryption_client(client_mock, encryption_client_mock, key_provider_mock):
    # Arrange
    environ["KEYALIAS"] = "dave"
    kms_client = MagicMock()
    key = {"KeyMetadata": {"Arn": "somearn"}}
    kms_client.describe_key.return_value = key

    client_mock.return_value = kms_client
    # Act
    initialise_encryption_client()
    # Assert
    kms_client.describe_key.assert_called_once_with(KeyId="alias/dave", GrantTokens=["string"])
    key_provider_mock.assert_called_once_with(key_ids=["somearn"])
    del environ["KEYALIAS"]
