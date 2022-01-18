from unittest.mock import MagicMock, patch
from application.common.aws import get_secret
from botocore.exceptions import ClientError
from json import loads
from os import environ
from pytest import raises

FILE_PATH = "application.common.aws"


@patch(f"{FILE_PATH}.client")
def test_get_secret(client_mock):
    # Arrangement
    environ["AWS_REGION"] = "eu-west-2"
    sm_client = MagicMock()
    secret = {"SecretString": '{"username": "dummy_username", "password": "dummy_password"}'}
    sm_client.get_secret_value.return_value = secret
    client_mock.return_value = sm_client
    # Act
    secret_name = "dummy_name"
    return_value = get_secret(secret_name)
    # Assert
    assert return_value == loads(secret["SecretString"])
    client_mock.assert_called_with(service_name="secretsmanager", region_name=environ["AWS_REGION"])
    sm_client.get_secret_value(SecretId=secret_name)
    # Clean up
    del environ["AWS_REGION"]


@patch(f"{FILE_PATH}.logger")
@patch(f"{FILE_PATH}.client")
def test_get_secret_expectation(client_mock, logger_mock):
    # Arrangement
    environ["AWS_REGION"] = "eu-west-2"
    sm_client = MagicMock()
    secret = {"SecretString": '{"username": "dummy_username", "password": "dummy_password"}'}
    sm_client.get_secret_value.return_value = secret
    client_mock.return_value = sm_client
    secret_name = "dummy_name"
    error = {"Error": {"Code": "dummy_code", "Message": "Dummy error msg"}}
    sm_client.get_secret_value.side_effect = ClientError({"Error": error}, operation_name="secret_manager")
    # Act
    with raises(ClientError):
        get_secret(secret_name)
    # Assert
    client_mock.assert_called_with(service_name="secretsmanager", region_name=environ["AWS_REGION"])
    logger_mock.exception.assert_called_with(f"Failed getting secret {secret_name}")
    # Clean up
    del environ["AWS_REGION"]
