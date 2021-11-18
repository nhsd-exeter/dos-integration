from ..put_message import add_message_to_service_bus
from os import environ
from unittest.mock import patch


@patch("application.put_message.post")
def test_add_message_to_service_bus(mock_post):
    # Arrange
    test_url = "https://test.com"
    environ["AZURE_SERVICE_BUS_ADD_MESSAGE_URL"] = test_url
    # Act
    add_message_to_service_bus()
    # Assert
    mock_post.assert_called_with(
        url=test_url,
        headers={
            "content-type": "application/json;charset=UTF-8",
        },
        json="{'key':'value'}",
    )
