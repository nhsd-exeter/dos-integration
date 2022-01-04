import os
from random import choices, randint, uniform
import json
from pathlib import Path

from pytest import fixture
from testfixtures import LogCapture

from ..dos import DoSLocation, DoSService
from ..opening_times import StandardOpeningTimes
import boto3
from moto import mock_dynamodb2
from os import environ

std_event_path = os.path.join(Path(__file__).parent.resolve(), "STANDARD_EVENT.json")
with open(std_event_path, "r") as file:
    PHARMACY_STANDARD_EVENT = json.load(file)


@fixture()
def log_capture():
    with LogCapture(names="lambda") as capture:
        yield capture


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
    environ["AWS_ACCESS_KEY_ID"] = "testing"
    environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    environ["AWS_SECURITY_TOKEN"] = "testing"
    environ["AWS_SESSION_TOKEN"] = "testing"
    environ["CHANGE_EVENTS_TABLE_NAME"] = "CHANGE_EVENTS_TABLE"
    environ["AWS_REGION"] = "us-east-2"


@fixture
def dynamodb_client(aws_credentials):
    with mock_dynamodb2():
        conn = boto3.client("dynamodb", region_name=environ["AWS_REGION"])
        yield conn
