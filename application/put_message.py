from os import environ
from requests import post


def add_message_to_service_bus() -> None:
    post(
        url=environ["AZURE_SERVICE_BUS_ADD_MESSAGE_URL"],
        headers={
            "content-type": "application/json;charset=UTF-8",
        },
        json="{'key':'value'}",
    )


if __name__ == "__main__":
    add_message_to_service_bus()
