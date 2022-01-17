from dataclasses import dataclass
from json import dumps
from os import environ
from random import choices
from aws_lambda_powertools import Logger
from unittest.mock import patch

from pytest import fixture

from ..event_processor import EventProcessor, lambda_handler, EXPECTED_ENVIRONMENT_VARIABLES
from ..nhs import NHSEntity
from .conftest import dummy_dos_service, dummy_dos_location
from ..change_request import (
    ADDRESS_CHANGE_KEY,
    PHONE_CHANGE_KEY,
    POSTCODE_CHANGE_KEY,
    PUBLICNAME_CHANGE_KEY,
    WEBSITE_CHANGE_KEY,
    ChangeRequest,
)
from dos import dos_location_cache

FILE_PATH = "application.event_processor.event_processor"


@fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = "event-processor"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:event-processor"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()


def test__init__():
    # Arrange
    test_data = {}
    for i in range(10):
        random_str = "".join(choices("ABCDEFGHIJKLM", k=8))
        test_data[random_str] = random_str
    test_data["OpeningTimes"] = [
        {
            "Weekday": "Friday",
            "Times": "08:45-17:00",
            "OffsetOpeningTime": 525,
            "OffsetClosingTime": 1020,
            "OpeningTimeType": "General",
            "AdditionalOpeningDate": "",
            "IsOpen": True,
        },
        {
            "Weekday": "Friday",
            "Times": "08:45-17:00",
            "OffsetOpeningTime": 525,
            "OffsetClosingTime": 1020,
            "OpeningTimeType": "Surgery",
            "AdditionalOpeningDate": "",
            "IsOpen": True,
        },
    ]
    nhs_entity = NHSEntity(test_data)
    # Act
    event_processor = EventProcessor(nhs_entity)
    # Assert
    assert event_processor.nhs_entity == nhs_entity
    assert isinstance(event_processor.matching_services, type(None))
    assert isinstance(event_processor.change_requests, type(None))
    assert event_processor.matching_services is None
    assert event_processor.change_requests is None


def test_get_change_requests_full_change_request():
    # Arrange
    service_1 = dummy_dos_service()
    service_1.id = 1
    service_1.uid = 101
    service_1.odscode = "SLC4501"
    service_1.web = "www.fakesite.com"
    service_1.publicphone = "01462622435"
    service_1.postcode = "S45 1AB"

    nhs_entity = NHSEntity({})
    nhs_entity.odscode = "SLC45"
    nhs_entity.website = "www.site.com"
    nhs_entity.phone = "01462622435"
    nhs_entity.postcode = "S45 1AA"
    nhs_entity.org_name = "Fake NHS Service"
    nhs_entity.address_lines = ["Fake Street1", "Fake Street2", "Fake Street3", "Fake City", "Fake County"]
    nhs_entity.OpeningTimes = []

    event_processor = EventProcessor(nhs_entity)
    event_processor.matching_services = [service_1]

    dos_location = dummy_dos_location()
    dos_location.postcode = nhs_entity.postcode
    dos_location_cache[dos_location.normal_postcode()] = [dos_location]

    # Act
    change_requests = event_processor.get_change_requests()
    # Assert
    assert (
        len(change_requests) == 1
    ), f"Should have 1 change request but more found: {len(change_requests)} change requests"

    cr = change_requests[0]
    for field in ["system", "service_id", "changes"]:
        assert hasattr(cr, field), f"Attribute {field} not found in change request"

    assert cr.system == "DoS Integration", f"System should be DoS Integration but is {cr.system}"

    expected_changes = {
        WEBSITE_CHANGE_KEY: nhs_entity.website,
        POSTCODE_CHANGE_KEY: nhs_entity.postcode,
        PUBLICNAME_CHANGE_KEY: nhs_entity.org_name,
        ADDRESS_CHANGE_KEY: nhs_entity.address_lines,
    }
    assert cr.changes == expected_changes, f"Changes should be {expected_changes} but they are {cr.changes}"


@patch(f"{FILE_PATH}.get_matching_dos_services")
def test_get_matching_services(mock_get_matching_dos_services, change_event):
    # Arrange
    nhs_entity = NHSEntity(change_event)
    service = dummy_dos_service()
    service.typeid = 13
    service.statusid = 1
    mock_get_matching_dos_services.return_value = [service]
    event_processor = EventProcessor(nhs_entity)
    # Act
    matching_services = event_processor.get_matching_services()
    # Assert
    assert matching_services == [service]


@patch.object(Logger, "get_correlation_id", return_value=1)
@patch(f"{FILE_PATH}.client")
def test_send_changes(mock_client, get_correlation_id_mock):
    # Arrange
    bus_name = "test"
    environ["EVENTBRIDGE_BUS_NAME"] = bus_name

    change_request = ChangeRequest(service_id=49016)
    change_request.reference = "1"
    change_request.system = "Profile Updater (test)"
    change_request.message = "Test message 1531816592293|@./"
    change_request.changes = {
        PHONE_CHANGE_KEY: "0118 999 88199 9119 725 3",
        WEBSITE_CHANGE_KEY: "https://www.google.pl",
    }

    nhs_entity = NHSEntity({})
    nhs_entity.odscode = "SLC45"
    nhs_entity.website = "www.site.com"
    nhs_entity.phone = "01462622435"
    nhs_entity.postcode = "S45 1AA"
    nhs_entity.org_name = "Fake NHS Service"
    nhs_entity.address_lines = ["Fake Street1", "Fake Street2", "Fake Street3", "Fake City", "Fake County"]

    event_processor = EventProcessor(nhs_entity)
    event_processor.change_requests = [change_request]
    # Act
    event_processor.send_changes()
    # Assert
    mock_client.assert_called_with("events")
    entry_details = {"change_payload": change_request.create_payload(), "correlation_id": 1}
    mock_client.return_value.put_events.assert_called_with(
        Entries=[
            {
                "Source": "event-processor",
                "DetailType": "change-request",
                "Detail": dumps(entry_details),
                "EventBusName": bus_name,
            },
        ]
    )
    # Clean up
    del environ["EVENTBRIDGE_BUS_NAME"]


@patch(f"{FILE_PATH}.get_latest_sequence_id_for_a_given_odscode_from_dynamodb")
@patch(f"{FILE_PATH}.add_change_request_to_dynamodb")
@patch(f"{FILE_PATH}.is_mock_mode")
@patch(f"{FILE_PATH}.EventProcessor")
@patch(f"{FILE_PATH}.NHSEntity")
@patch(f"{FILE_PATH}.extract_body")
def test_lambda_handler_unmatched_service(
    mock_extract_body,
    mock_nhs_entity,
    mock_event_processor,
    mock_is_mock_mode,
    mock_add_change_request_to_dynamodb,
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb,
    change_event,
    lambda_context,
):
    # Arrange
    mock_entity = NHSEntity(change_event)
    sqs_event = SQS_EVENT.copy()
    sqs_event["Records"][0]["body"] = dumps(change_event)
    mock_extract_body.return_value = change_event
    mock_nhs_entity.return_value = mock_entity
    mock_is_mock_mode.return_value = False
    mock_add_change_request_to_dynamodb.return_value = None
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb.return_value = 0
    for env in EXPECTED_ENVIRONMENT_VARIABLES:
        environ[env] = "test"
    # Act
    response = lambda_handler(sqs_event, lambda_context)
    # Assert
    assert response is None, f"Response should be None but is {response}"
    mock_extract_body.assert_called_once_with(sqs_event["Records"][0]["body"])
    mock_nhs_entity.assert_called_once_with(change_event)
    mock_event_processor.assert_called_once_with(mock_entity)

    mock_event_processor.send_changes.assert_not_called()
    # Clean up
    for env in EXPECTED_ENVIRONMENT_VARIABLES:
        del environ[env]


@patch.object(Logger, "error")
@patch(f"{FILE_PATH}.add_change_request_to_dynamodb")
@patch(f"{FILE_PATH}.get_latest_sequence_id_for_a_given_odscode_from_dynamodb")
@patch(f"{FILE_PATH}.is_mock_mode")
@patch(f"{FILE_PATH}.EventProcessor")
@patch(f"{FILE_PATH}.NHSEntity")
@patch(f"{FILE_PATH}.extract_body")
def test_lambda_handler_no_sequence_number(
    mock_extract_body,
    mock_nhs_entity,
    mock_event_processor,
    mock_is_mock_mode,
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb,
    mock_add_change_request_to_dynamodb,
    mock_logger,
    change_event,
    lambda_context,
):
    # Arrange
    mock_entity = NHSEntity(change_event)
    sqs_event = SQS_EVENT.copy()
    sqs_event["Records"][0]["body"] = dumps(change_event)
    del sqs_event["Records"][0]["messageAttributes"]["sequence-number"]
    mock_extract_body.return_value = change_event
    mock_nhs_entity.return_value = mock_entity
    mock_is_mock_mode.return_value = False
    mock_add_change_request_to_dynamodb.return_value = None
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb.return_value = 0
    for env in EXPECTED_ENVIRONMENT_VARIABLES:
        environ[env] = "test"
    # Act
    response = lambda_handler(sqs_event, lambda_context)
    # Assert
    assert response is None, f"Response should be None but is {response}"
    mock_is_mock_mode.assert_called_once
    mock_nhs_entity.assert_not_called()
    mock_event_processor.assert_not_called()
    mock_event_processor.send_changes.assert_not_called()
    mock_logger.assert_called_with("No sequence number provided, so message will be ignored.")
    # Clean up
    for env in EXPECTED_ENVIRONMENT_VARIABLES:
        del environ[env]


@patch.object(Logger, "error")
@patch(f"{FILE_PATH}.add_change_request_to_dynamodb")
@patch(f"{FILE_PATH}.get_latest_sequence_id_for_a_given_odscode_from_dynamodb")
@patch(f"{FILE_PATH}.get_sequence_number")
@patch(f"{FILE_PATH}.is_mock_mode")
@patch(f"{FILE_PATH}.EventProcessor")
@patch(f"{FILE_PATH}.NHSEntity")
@patch(f"{FILE_PATH}.extract_body")
def test_lambda_handler_sequence_number_is_less_than_db_sequence_number(
    mock_extract_body,
    mock_nhs_entity,
    mock_event_processor,
    mock_is_mock_mode,
    mock_get_sequence_number,
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb,
    mock_add_change_request_to_dynamodb,
    mock_logger,
    change_event,
    lambda_context,
):
    # Arrange
    mock_entity = NHSEntity(change_event)
    sqs_event = SQS_EVENT.copy()
    sqs_event["Records"][0]["body"] = dumps(change_event)
    mock_extract_body.return_value = change_event
    mock_nhs_entity.return_value = mock_entity
    mock_is_mock_mode.return_value = False
    mock_add_change_request_to_dynamodb.return_value = None
    mock_get_sequence_number.return_value = 1
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb.return_value = 3
    for env in EXPECTED_ENVIRONMENT_VARIABLES:
        environ[env] = "test"
    # Act
    response = lambda_handler(sqs_event, lambda_context)
    # Assert
    assert response is None, f"Response should be None but is {response}"
    mock_is_mock_mode.assert_called_once
    mock_nhs_entity.assert_not_called()
    mock_event_processor.assert_not_called()
    mock_event_processor.send_changes.assert_not_called()
    mock_logger.assert_called_with(
        "Sequence id is smaller than the existing one in db for a given odscode, so will be ignored"
    )
    # Clean up
    for env in EXPECTED_ENVIRONMENT_VARIABLES:
        del environ[env]


SQS_EVENT = {
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
                "correlation-id": {"stringValue": "1", "dataType": "String"},
                "sequence-number": {"stringValue": "1", "dataType": "Number"},
            },
            "md5OfBody": "e4e68fb7bd0e697a0ae8f1bb342846b3",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:my-queue",
            "awsRegion": "us-east-2",
        }
    ]
}
