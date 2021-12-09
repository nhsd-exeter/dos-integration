from os import environ
from unittest.mock import MagicMock, patch
from pytest import raises

from requests.auth import HTTPBasicAuth
from responses import POST, activate, add

from ..change_request import ChangeRequest

FILE_PATH = "application.event_sender.change_request"


class TestChangeRequest:
    CHANGE_REQUEST_EVENT = {
        "reference": "1",
        "system": "Profile Updater (test)",
        "message": "Test message 1531816592293|@./",
        "service_id": "49016",
        "changes": {"ods_code": "f0000", "phone": "0118 999 88199 9119 725 3", "website": "https://www.google.pl"},
    }
    WEBSITE = "https://test.com"
    TIMEOUT = "10"
    USERNAME = "username"
    PASSWORD = "password"

    def test__init__(self):
        # Arrange
        environ["PROFILE"] = "remote"
        environ["DOS_API_GATEWAY_URL"] = self.WEBSITE
        environ["DOS_API_GATEWAY_REQUEST_TIMEOUT"] = self.TIMEOUT
        environ["DOS_API_GATEWAY_USERNAME"] = self.USERNAME
        environ["DOS_API_GATEWAY_PASSWORD"] = self.PASSWORD
        expected_auth = HTTPBasicAuth(self.USERNAME, self.PASSWORD)
        # Act
        change_request = ChangeRequest(self.CHANGE_REQUEST_EVENT)
        # Assert
        assert change_request.headers == {"Content-Type": "application/json", "Accept": "application/json"}
        assert change_request.change_request_url == self.WEBSITE
        assert change_request.timeout == int(self.TIMEOUT)
        assert change_request.authorisation == expected_auth
        assert change_request.change_request_body == self.CHANGE_REQUEST_EVENT
        # Clean up
        del environ["DOS_API_GATEWAY_URL"]
        del environ["DOS_API_GATEWAY_REQUEST_TIMEOUT"]
        del environ["DOS_API_GATEWAY_USERNAME"]
        del environ["DOS_API_GATEWAY_PASSWORD"]
        del environ["PROFILE"]

    @activate
    def test_post_change_request(self):
        # Arrange
        environ["PROFILE"] = "remote"
        environ["DOS_API_GATEWAY_URL"] = self.WEBSITE
        environ["DOS_API_GATEWAY_REQUEST_TIMEOUT"] = self.TIMEOUT
        environ["DOS_API_GATEWAY_USERNAME"] = self.USERNAME
        environ["DOS_API_GATEWAY_PASSWORD"] = self.PASSWORD
        change_request = ChangeRequest(self.CHANGE_REQUEST_EVENT)
        expected_response_body = {"my-key": "my-val"}
        status_code = 200
        add(POST, self.WEBSITE, json=expected_response_body, status=status_code)
        change_request.change_request_logger = MagicMock()
        # Act
        change_request.post_change_request()
        # Assert
        assert change_request.response.status_code == status_code
        change_request.change_request_logger.log_change_request_response.assert_called_once_with(
            change_request.response
        )
        # Clean up
        del environ["DOS_API_GATEWAY_URL"]
        del environ["DOS_API_GATEWAY_REQUEST_TIMEOUT"]
        del environ["DOS_API_GATEWAY_USERNAME"]
        del environ["DOS_API_GATEWAY_PASSWORD"]
        del environ["PROFILE"]

    @patch(f"{FILE_PATH}.post")
    def test_post_change_request_exception(self, mock_post):
        # Arrange
        environ["PROFILE"] = "remote"
        environ["DOS_API_GATEWAY_URL"] = self.WEBSITE
        environ["DOS_API_GATEWAY_REQUEST_TIMEOUT"] = self.TIMEOUT
        environ["DOS_API_GATEWAY_USERNAME"] = self.USERNAME
        environ["DOS_API_GATEWAY_PASSWORD"] = self.PASSWORD
        change_request = ChangeRequest(self.CHANGE_REQUEST_EVENT)
        change_request.change_request_logger = MagicMock()
        mock_post.side_effect = Exception("Test exception")
        # Act & Assert
        with raises(Exception):
            change_request.post_change_request()
        # Clean up
        del environ["DOS_API_GATEWAY_URL"]
        del environ["DOS_API_GATEWAY_REQUEST_TIMEOUT"]
        del environ["DOS_API_GATEWAY_USERNAME"]
        del environ["DOS_API_GATEWAY_PASSWORD"]
        del environ["PROFILE"]
