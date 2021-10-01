from azure.servicebus import ServiceBusClient
from os import environ


def get_message_from_service_bus() -> None:
    with ServiceBusClient.from_connection_string(
        conn_str=environ["AZURE_SERVICE_BUS_CONNECTION_STRING"],
        logging_enable=True,
    ) as service_bus_client:
        print("ServiceBusClient set")
        with service_bus_client.get_subscription_receiver(
            topic_name=environ["AZURE_SERVICE_BUS_TOPIC_NAME"],
            subscription_name=environ["AZURE_SERVICE_BUS_SUBSCRIPTION_NAME"],
        ) as service_bus_receiver:
            print("Topic and Subscription Name set")
            received_msgs = service_bus_receiver.peek_messages(max_message_count=30)
            print("Received messages if any")
            print(received_msgs)


if __name__ == "__main__":
    get_message_from_service_bus()
