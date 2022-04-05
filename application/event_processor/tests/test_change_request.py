from ..change_request import ChangeRequest
from aws_lambda_powertools import Logger

logger = Logger()


class TestChangeRequest:
    service_id = 123456789
    odscode = "FD189"
    correlation_id = "dummy_correlation_id"
    changes = {"website": "https://test.com"}

    def test__init__(self):
        # Arrange
        expected_change_requests = {
            "reference": str(self.correlation_id),
            "system": "DoS Integration",
            "message": f"DoS Integration CR. correlation-id: {self.correlation_id}",
            "replace_opening_dates_mode": True,
            "service_id": str(self.service_id),
            "odscode": self.odscode,
            "changes": self.changes,
        }
        logger.set_correlation_id(self.correlation_id)
        # Act
        change_request = ChangeRequest(self.service_id, self.odscode, self.changes)
        # Assert
        assert expected_change_requests == {
            "reference": change_request.reference,
            "system": change_request.system,
            "message": change_request.message,
            "replace_opening_dates_mode": change_request.replace_opening_dates_mode,
            "service_id": str(change_request.service_id),
            "odscode": change_request.odscode,
            "changes": change_request.changes,
        }

    def test_get_change_request(self):
        # Arrange
        expected_change_requests = {
            "reference": str(self.correlation_id),
            "system": "DoS Integration",
            "message": f"DoS Integration CR. correlation-id: {self.correlation_id}",
            "replace_opening_dates_mode": True,
            "service_id": str(self.service_id),
            "odscode": self.odscode,
            "changes": self.changes,
        }
        logger.set_correlation_id(self.correlation_id)
        # Act
        change_request = ChangeRequest(self.service_id, self.odscode, self.changes)
        # Assert
        assert expected_change_requests == change_request.create_payload()
