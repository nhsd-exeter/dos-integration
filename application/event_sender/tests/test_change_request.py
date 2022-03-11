from os import environ
from unittest.mock import MagicMock, patch
from aws_lambda_powertools import Logger
from requests.auth import HTTPBasicAuth
from responses import POST, activate, add

from event_sender import change_request
from event_sender.change_request import ChangeRequest

FILE_PATH = "application.event_sender.change_request"


class TestChangeRequest:
    CHANGE_REQUEST_EVENT = {
        "reference": "1",
        "system": "Profile Updater (test)",
        "message": "Test message 1531816592293|@./",
        "service_id": "49016",
        "changes": {"ods_code": "f0000", "phone": "0118 999 88199 9119 725 3", "website": "https://www.google.pl"},
    }
    CORRELATION_ID = 1
    WEBSITE = "https://test.com"
    TIMEOUT = "10"
    USERNAME_KEY = "username_sm_key"
    PASSWORD_KEY = "password_sm_key"
    SECRETS = {USERNAME_KEY: "username", PASSWORD_KEY: "password"}
    AWS_SM_API_GATEWAY_SECRET = "api-gateway-secrets"

    @patch.object(change_request, "get_secret", return_value=SECRETS)
    def test__init__(self, get_secret_mock):
        # Arrange
        environ["PROFILE"] = "remote"
        environ["DOS_API_GATEWAY_URL"] = self.WEBSITE
        environ["DOS_API_GATEWAY_REQUEST_TIMEOUT"] = self.TIMEOUT
        environ["DOS_API_GATEWAY_USERNAME_KEY"] = self.USERNAME_KEY
        environ["DOS_API_GATEWAY_PASSWORD_KEY"] = self.PASSWORD_KEY
        environ["DOS_API_GATEWAY_SECRETS"] = self.AWS_SM_API_GATEWAY_SECRET
        expected_auth = HTTPBasicAuth(self.SECRETS[self.USERNAME_KEY], self.SECRETS[self.PASSWORD_KEY])
        # Act
        change_request = ChangeRequest(self.CHANGE_REQUEST_EVENT)
        # Assert
        assert change_request.headers == {"Content-Type": "application/json", "Accept": "application/json"}
        assert change_request.change_request_url == self.WEBSITE
        assert change_request.timeout == int(self.TIMEOUT)
        assert change_request.authorisation == expected_auth
        assert change_request.change_request_body == self.CHANGE_REQUEST_EVENT
        assert change_request.headers == {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        get_secret_mock.assert_called_with(self.AWS_SM_API_GATEWAY_SECRET)
        # Clean up
        del environ["DOS_API_GATEWAY_URL"]
        del environ["DOS_API_GATEWAY_REQUEST_TIMEOUT"]
        del environ["DOS_API_GATEWAY_USERNAME_KEY"]
        del environ["DOS_API_GATEWAY_PASSWORD_KEY"]
        del environ["PROFILE"]

    @patch.object(Logger, "get_correlation_id", return_value="CORRELATION")
    @patch.object(change_request, "get_secret", return_value=SECRETS)
    def test__init__with_correlation_id(self, get_secret_mock, get_correlation_id_mock):
        # Arrange
        environ["PROFILE"] = "remote"
        environ["DOS_API_GATEWAY_URL"] = self.WEBSITE
        environ["DOS_API_GATEWAY_REQUEST_TIMEOUT"] = self.TIMEOUT
        environ["DOS_API_GATEWAY_USERNAME_KEY"] = self.USERNAME_KEY
        environ["DOS_API_GATEWAY_PASSWORD_KEY"] = self.PASSWORD_KEY
        expected_auth = HTTPBasicAuth(self.SECRETS[self.USERNAME_KEY], self.SECRETS[self.PASSWORD_KEY])
        # Act
        change_request = ChangeRequest(self.CHANGE_REQUEST_EVENT)
        # Assert
        assert change_request.headers == {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        assert change_request.change_request_url == self.WEBSITE
        assert change_request.timeout == int(self.TIMEOUT)
        assert change_request.authorisation == expected_auth
        assert change_request.change_request_body == self.CHANGE_REQUEST_EVENT
        get_secret_mock.assert_called_with(self.AWS_SM_API_GATEWAY_SECRET)
        # Clean up
        del environ["DOS_API_GATEWAY_URL"]
        del environ["DOS_API_GATEWAY_REQUEST_TIMEOUT"]
        del environ["DOS_API_GATEWAY_USERNAME_KEY"]
        del environ["DOS_API_GATEWAY_PASSWORD_KEY"]
        del environ["PROFILE"]

    @patch.object(change_request, "get_secret", return_value=SECRETS)
    @activate
    def test_post_change_request(self, get_secret_mock):
        # Arrange
        environ["PROFILE"] = "remote"
        environ["DOS_API_GATEWAY_URL"] = self.WEBSITE
        environ["DOS_API_GATEWAY_REQUEST_TIMEOUT"] = self.TIMEOUT
        environ["DOS_API_GATEWAY_USERNAME_KEY"] = self.USERNAME_KEY
        environ["DOS_API_GATEWAY_PASSWORD_KEY"] = self.PASSWORD_KEY
        change_request = ChangeRequest(self.CHANGE_REQUEST_EVENT)
        expected_response_body = {"my-key": "my-val"}
        status_code = 201
        add(POST, self.WEBSITE, json=expected_response_body, status=status_code)
        change_request.change_request_logger = MagicMock()
        # Act
        response = change_request.post_change_request(False)
        # Assert
        get_secret_mock.assert_called_with(self.AWS_SM_API_GATEWAY_SECRET)
        assert response.status_code == status_code
        change_request.change_request_logger.log_change_request_response.assert_called_once_with(response)
        # Clean up
        del environ["DOS_API_GATEWAY_URL"]
        del environ["DOS_API_GATEWAY_REQUEST_TIMEOUT"]
        del environ["DOS_API_GATEWAY_USERNAME_KEY"]
        del environ["DOS_API_GATEWAY_PASSWORD_KEY"]
        del environ["PROFILE"]

    @patch.object(change_request, "post", side_effect=Exception("Test exception"))
    @patch.object(change_request, "get_secret", return_value=SECRETS)
    def test_post_change_request_exception(self, get_secret_mock, mock_post):
        # Arrange
        environ["PROFILE"] = "remote"
        environ["DOS_API_GATEWAY_URL"] = self.WEBSITE
        environ["DOS_API_GATEWAY_REQUEST_TIMEOUT"] = self.TIMEOUT
        environ["DOS_API_GATEWAY_USERNAME_KEY"] = self.USERNAME_KEY
        environ["DOS_API_GATEWAY_PASSWORD_KEY"] = self.PASSWORD_KEY
        change_request = ChangeRequest(self.CHANGE_REQUEST_EVENT)
        cr_logger_mock = MagicMock()
        change_request.change_request_logger = cr_logger_mock
        mock_post.side_effect = Exception("Test exception")
        # Act
        change_request.post_change_request(False)
        # Assert
        mock_post.assert_called()
        cr_logger_mock.log_change_request_exception.assert_called()
        cr_logger_mock.log_change_request_response.assert_not_called()
        # Clean up
        del environ["DOS_API_GATEWAY_URL"]
        del environ["DOS_API_GATEWAY_REQUEST_TIMEOUT"]
        del environ["DOS_API_GATEWAY_USERNAME_KEY"]
        del environ["DOS_API_GATEWAY_PASSWORD_KEY"]
        del environ["PROFILE"]
