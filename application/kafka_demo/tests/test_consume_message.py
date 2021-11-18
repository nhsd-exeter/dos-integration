from kafka_demo.consume_message import get_message_from_service_bus
from os import environ
from unittest.mock import MagicMock, patch


@patch("kafka_demo.consume_message.ServiceBusClient")
def test_add_message_to_service_bus(mock_service_bus_client):
    # Arrange
    connection_string = "https://test.com"
    topic_name = "topic_name"
    subscription_name = "subscription_name"
    service_bus_client = MagicMock()
    environ["AZURE_SERVICE_BUS_CONNECTION_STRING"] = connection_string
    environ["AZURE_SERVICE_BUS_TOPIC_NAME"] = topic_name
    environ["AZURE_SERVICE_BUS_SUBSCRIPTION_NAME"] = subscription_name
    mock_service_bus_client.from_connection_string.return_value = service_bus_client
    # Act
    get_message_from_service_bus()
    # Assert
    mock_service_bus_client.from_connection_string.assert_called_with(conn_str=connection_string, logging_enable=True)
    service_bus_client.__enter__().get_subscription_receiver.assert_called_with(
        topic_name=topic_name, subscription_name=subscription_name
    )
    service_bus_client.__enter__().get_subscription_receiver().__enter__().receive_messages.assert_called_with(
        max_message_count=10, max_wait_time=5
    )
