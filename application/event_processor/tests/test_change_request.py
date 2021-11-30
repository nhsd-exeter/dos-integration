from ..change_request import ChangeRequest


class TestChangeRequest:
    service_id = 123456789
    trace_id = "<NO-TRACE-ID>"
    changes = {"website": "https://test.com"}

    def test__init__(self):
        # Arrange
        expected_change_requests = {
            "reference": str(self.trace_id),
            "system": "DoS Integration",
            "message": f"DoS Integration CR. AMZN-trace-id: {self.trace_id}",
            "service_id": str(self.service_id),
            "changes": self.changes,
        }
        # Act
        change_request = ChangeRequest(self.service_id, self.changes)
        # Assert
        assert expected_change_requests == {
            "reference": change_request.reference,
            "system": change_request.system,
            "message": change_request.message,
            "service_id": str(change_request.service_id),
            "changes": change_request.changes,
        }

    def test_get_change_request(self):
        # Arrange
        expected_change_requests = {
            "reference": str(self.trace_id),
            "system": "DoS Integration",
            "message": f"DoS Integration CR. AMZN-trace-id: {self.trace_id}",
            "service_id": str(self.service_id),
            "changes": self.changes,
        }
        # Act
        change_request = ChangeRequest(self.service_id, self.changes)
        # Assert
        assert expected_change_requests == change_request.create_payload()
