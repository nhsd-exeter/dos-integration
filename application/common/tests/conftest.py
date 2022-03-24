import json
import os
from random import choices, randint, uniform

import boto3
from moto import mock_dynamodb2
from pytest import fixture

from ..dos import DoSLocation, DoSService
from ..opening_times import StandardOpeningTimes

std_event_path = "event_processor/tests/STANDARD_EVENT.json"

with open(std_event_path, "r") as file:
    PHARMACY_STANDARD_EVENT = json.load(file)


def dummy_dos_service() -> DoSService:
    """Creates a DoSService Object with random data for the unit testing"""
    test_data = []
    for col in DoSService.db_columns:
        random_str = "".join(choices("ABCDEFGHIJKLM", k=8))
        test_data.append(random_str)
    dos_service = DoSService(test_data)
    dos_service._standard_opening_times = StandardOpeningTimes()
    dos_service._specified_opening_times = []
    return dos_service


def dummy_dos_location() -> DoSLocation:
    """Creates a DoSLocation Object with random data for the unit testing"""
    return DoSLocation(
        id=randint(1111, 9999),
        postcode="".join(choices("01234567890ABCDEFGHIJKLM", k=6)),
        easting=randint(1111, 9999),
        northing=randint(1111, 9999),
        latitude=uniform(-200.0, 200.0),
        longitude=uniform(-200.0, 200.0),
        postaltown="".join(choices("ABCDEFGHIJKLM", k=8)),
    )


@fixture
def change_event():
    change_event = PHARMACY_STANDARD_EVENT.copy()
    yield change_event


@fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["CHANGE_EVENTS_TABLE_NAME"] = "CHANGE_EVENTS_TABLE"
    os.environ["AWS_REGION"] = "us-east-2"


@fixture
def dynamodb_client(aws_credentials):
    with mock_dynamodb2():
        conn = boto3.client("dynamodb", region_name=os.environ["AWS_REGION"])
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
