from json import dumps

import boto3
import pytest
from moto import mock_aws

FILE_PATH = "application.common.secretsmanager"


@mock_aws
def test_get_secret() -> None:
    from application.common.secretsmanager import get_secret

    # Arrangement
    secret_name = "dummy_name"
    secret = {"username": "dummy_username", "password": "dummy_password"}
    sm = boto3.client("secretsmanager")
    sm.create_secret(Name=secret_name, SecretString=dumps(secret))
    # Act
    return_value = get_secret(secret_name=secret_name)
    # Assert
    assert return_value == secret


@mock_aws
def test_get_secret_resource_not_found() -> None:
    from application.common.secretsmanager import get_secret

    with pytest.raises(Exception, match="Failed getting secret 'fake_secret_name' from secrets manager"):
        get_secret("fake_secret_name")
