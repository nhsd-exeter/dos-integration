import json
from dataclasses import dataclass
from os import environ
from random import choices, randint, uniform
from typing import Any

import pytest
from aws_lambda_powertools.utilities.typing import LambdaContext
from boto3 import Session
from moto import mock_dynamodb
from testfixtures import LogCapture

from application.common.dos import DoSLocation, DoSService
from application.common.opening_times import StandardOpeningTimes

STD_EVENT_PATH = "application/test_resources/STANDARD_EVENT.json"
with open(STD_EVENT_PATH, encoding="utf8") as file:
    PHARMACY_STANDARD_EVENT = json.load(file)

STD_EVENT_STAFF_PATH = "application/test_resources/STANDARD_EVENT_WITH_STAFF.json"
with open(STD_EVENT_STAFF_PATH, encoding="utf8") as file:
    PHARMACY_STANDARD_EVENT_STAFF = json.load(file)


@pytest.fixture(autouse=True)
def _reset_standard_change_event() -> None:
    """Reset the standard change event to its original state."""
    with open(STD_EVENT_PATH, encoding="utf8") as file:
        PHARMACY_STANDARD_EVENT.clear()
        PHARMACY_STANDARD_EVENT.update(json.load(file))


def get_std_event(**kwargs: Any) -> dict:  # noqa: ANN401
    """Creates a standard event with random data for the unit testing."""
    event = PHARMACY_STANDARD_EVENT.copy()
    for name, value in kwargs.items():
        if value is not None:
            event[name] = value
    return event


def dummy_dos_service(**kwargs: Any) -> DoSService:  # noqa: ANN401
    """Creates a DoSService Object with random data for the unit testing."""
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


def blank_dos_service(**kwargs: Any) -> DoSService:  # noqa: ANN401
    """Creates a DoSService Object with blank str data for the unit testing."""
    test_data = {col: "" for col in DoSService.field_names()}
    dos_service = DoSService(test_data)

    for name, value in kwargs.items():
        if value is not None:
            setattr(dos_service, name, value)

    return dos_service


def dummy_dos_location() -> DoSLocation:
    """Creates a DoSLocation Object with random data for the unit testing."""
    return DoSLocation(
        id=randint(1111, 9999),
        postcode="".join(choices("01234567890ABCDEFGHIJKLM", k=6)),
        easting=randint(1111, 9999),
        northing=randint(1111, 9999),
        postaltown="".join(choices("01234567890ABCDEFGHIJKLM", k=8)),
        latitude=uniform(-200.0, 200.0),
        longitude=uniform(-200.0, 200.0),
    )


@pytest.fixture()
def change_event() -> dict:
    """Generate a change event for testing."""
    return PHARMACY_STANDARD_EVENT.copy()


@pytest.fixture()
def change_event_staff() -> dict:
    """Get a standard change event with staff."""
    return PHARMACY_STANDARD_EVENT_STAFF.copy()


@pytest.fixture()
def _aws_credentials() -> None:
    """Mocked AWS Credentials for moto."""
    environ["AWS_ACCESS_KEY_ID"] = "testing"
    environ["AWS_SECRET_ACCESS_KEY"] = "testing"  # noqa: S105
    environ["AWS_SECURITY_TOKEN"] = "testing"  # noqa: S105
    environ["AWS_SESSION_TOKEN"] = "testing"  # noqa: S105
    environ["CHANGE_EVENTS_TABLE_NAME"] = "CHANGE_EVENTS_TABLE"
    environ["AWS_REGION"] = "us-east-2"


@pytest.fixture()
def dynamodb_client(boto_session: Any) -> Any:  # noqa: ANN401,
    """DynamoDB Client Class."""
    return boto_session.client("dynamodb", region_name=environ["AWS_REGION"])


@pytest.fixture()
def dynamodb_resource(boto_session: Any) -> Any:  # noqa: ANN401
    """DynamoDB Resource Class."""
    return boto_session.resource("dynamodb", region_name=environ["AWS_REGION"])


@pytest.fixture()
def boto_session(_aws_credentials: Any) -> Any:  # noqa: ANN401
    """Mocked AWS Credentials for moto."""
    with mock_dynamodb():
        yield Session()


@pytest.fixture()
def dead_letter_message() -> dict:
    """Generate a dead letter message for testing."""
    return {
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
            },
        ],
    }


@pytest.fixture()
def lambda_context() -> LambdaContext:
    """Generate a lambda context for testing."""

    @dataclass
    class LambdaContext:
        function_name: str = "lambda"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:lambda"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()


@pytest.fixture()
def log_capture() -> LogCapture:
    """Capture logs.

    Yields:
        LogCapture: Log capture
    """
    with LogCapture(names="lambda") as capture:
        yield capture


@pytest.fixture()
def dynamodb_table_create(dynamodb_client: Any) -> dict[str, Any]:  # noqa: ANN401
    """Create a DynamoDB CHANGE_EVENTS_TABLE table pytest.fixture."""
    return dynamodb_client.create_table(
        TableName=environ["CHANGE_EVENTS_TABLE_NAME"],
        BillingMode="PAY_PER_REQUEST",
        KeySchema=[
            {"AttributeName": "Id", "KeyType": "HASH"},
            {"AttributeName": "ODSCode", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "Id", "AttributeType": "S"},
            {"AttributeName": "ODSCode", "AttributeType": "S"},
            {"AttributeName": "SequenceNumber", "AttributeType": "N"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "gsi_ods_sequence",
                "KeySchema": [
                    {"AttributeName": "ODSCode", "KeyType": "HASH"},
                    {"AttributeName": "SequenceNumber", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
    )
