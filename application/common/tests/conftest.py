from pytest import fixture
import boto3
from moto import mock_dynamodb2
import os
import json

std_event_path = "event_processor/tests/STANDARD_EVENT.json"

with open(std_event_path, "r") as file:
    PHARMACY_STANDARD_EVENT = json.load(file)


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
