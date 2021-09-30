from os import environ
from requests import post

post(
    url=environ["AZURE_SERVICE_BUS_ADD_MESSAGE_URL"],
    headers={
        "content-type": "application/json;charset=UTF-8",
    },
    json="{'key':'value'}",
)
