from os import environ

from ..change_request import ChangeRequest


class TestChangeRequest:
    change_request_event = {
        "reference": "1",
        "system": "Profile Updater (test)",
        "message": "Test message 1531816592293|@./",
        "service_id": "49016",
        "changes": {"ods_code": "f0000", "phone": "0118 999 88199 9119 725 3", "website": "http://www.google.pl"},
    }

    def test__init__(self):
        # Arrange
        environ["CHANGE_REQUEST_ENDPOINT_URL"] = "dev"
        environ["CHANGE_REQUEST_ENDPOINT_TIMEOUT"] = "10"
        environ["API_GATEWAY_USERNAME"] = "dev"
        environ["API_GATEWAY_PASSWORD"] = "dev"
        # Act
        ChangeRequest(self.change_request_event)
        # Assert

    def test_post_change_request(self):
        pass

    def test_get_environment_variable(self):
        pass
