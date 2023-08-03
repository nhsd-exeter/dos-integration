from application.common.types import UpdateRequest


def test_update_request():
    # Arrange
    change_event = {"ODSCode": "12345"}
    service_id = "1"
    # Act
    response = UpdateRequest(change_event=change_event, service_id=service_id)
    # Assert
    assert change_event == response["change_event"]
    assert service_id == response["service_id"]
