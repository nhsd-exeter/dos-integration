from ..change_event_responses import set_return_value


def test_set_return_value():
    # Arrange
    status_code = 200
    message = "example"
    # Act
    response = set_return_value(status_code, message)
    # Assert
    assert response == {"statusCode": status_code, "body": '{"message": "' + message + '"}'}
