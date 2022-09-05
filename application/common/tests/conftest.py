import json
from dataclasses import dataclass
from os import environ
from random import choices, randint, uniform

from boto3 import client
from moto import mock_dynamodb
from pytest import fixture

from ..dos import DoSLocation, DoSService
from ..opening_times import StandardOpeningTimes

STD_EVENT_PATH = "application/service_matcher/tests/STANDARD_EVENT.json"

with open(STD_EVENT_PATH, "r", encoding="utf8") as file:
    PHARMACY_STANDARD_EVENT = json.load(file)


def dummy_dos_service(**kwargs) -> DoSService:
    """Creates a DoSService Object with random data for the unit testing"""
    test_data = {}
    for col in DoSService.field_names():
        random_str = "".join(choices("ABCDEFGHIJKLM", k=8))
        test_data[col] = random_str
    dos_service = DoSService(test_data)
    dos_service.standard_opening_times = StandardOpeningTimes()
    dos_service.specified_opening_times = []

    for name, value in kwargs.items():
        if value is not None:
            setattr(dos_service, name, value)

    return dos_service


def blank_dos_service(**kwargs) -> DoSService:
    """Creates a DoSService Object with blank str data for the unit testing"""
    test_data = {}
    for col in DoSService.field_names():
        test_data[col] = ""
    dos_service = DoSService(test_data)

    for name, value in kwargs.items():
        if value is not None:
            setattr(dos_service, name, value)

    return dos_service


def dummy_dos_location() -> DoSLocation:
    """Creates a DoSLocation Object with random data for the unit testing"""
    return DoSLocation(
        id=randint(1111, 9999),
        postcode="".join(choices("01234567890ABCDEFGHIJKLM", k=6)),
        easting=randint(1111, 9999),
        northing=randint(1111, 9999),
        postaltown="".join(choices("01234567890ABCDEFGHIJKLM", k=8)),
        latitude=uniform(-200.0, 200.0),
        longitude=uniform(-200.0, 200.0),
    )


@fixture
def change_event():
    change_event = PHARMACY_STANDARD_EVENT.copy()
    yield change_event


@fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    environ["AWS_ACCESS_KEY_ID"] = "testing"
    environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    environ["AWS_SECURITY_TOKEN"] = "testing"
    environ["AWS_SESSION_TOKEN"] = "testing"
    environ["CHANGE_EVENTS_TABLE_NAME"] = "CHANGE_EVENTS_TABLE"
    environ["AWS_REGION"] = "us-east-2"


@fixture
def dynamodb_client(aws_credentials):
    with mock_dynamodb():
        conn = client("dynamodb", region_name=environ["AWS_REGION"])
        yield conn


@fixture
def dead_letter_message():
    yield {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy0a...",
                "body": "Test message.",
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1545082649183",
                    "SenderId": "AIDAIENQZJOLO23YVJ4VO",
                    "ApproximateFirstReceiveTimestamp": "1545082649185",
                },
                "messageAttributes": {
                    "error_msg": {
                        "stringValue": "ApiDestination returned HTTP status 400 with payload: Dummy",
                        "stringListValues": [],
                        "binaryListValues": [],
                        "dataType": "String",
                    },
                    "error_msg_http_code": {
                        "stringValue": "400",
                        "stringListValues": [],
                        "binaryListValues": [],
                        "dataType": "Number",
                    },
                    "other": {
                        "stringValue": "other",
                        "stringListValues": [],
                        "binaryListValues": [],
                        "dataType": "other",
                    },
                    "correlation-id": {
                        "stringValue": "test",
                        "stringListValues": [],
                        "binaryListValues": [],
                        "dataType": "String",
                    },
                },
                "md5OfBody": "e4e68fb7bd0e697a0ae8f1bb342846b3",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:cr-fifo-dlq-queue",
                "awsRegion": "us-east-2",
            }
        ]
    }


@fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = "service-matcher"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:service-matcher"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()
