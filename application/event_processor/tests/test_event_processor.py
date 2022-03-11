from dataclasses import dataclass
from json import dumps
from os import environ
import hashlib
from random import choices
from aws_embedded_metrics.logger.metrics_logger import MetricsLogger
from aws_lambda_powertools import Logger
from unittest.mock import patch
import logging

from pytest import fixture, raises

from ..event_processor import EventProcessor, lambda_handler, EXPECTED_ENVIRONMENT_VARIABLES
from ..nhs import NHSEntity
from .conftest import dummy_dos_service, dummy_dos_location
from ..change_request import (
    ADDRESS_CHANGE_KEY,
    ADDRESS_LINES_KEY,
    PHONE_CHANGE_KEY,
    POSTCODE_CHANGE_KEY,
    PUBLICNAME_CHANGE_KEY,
    WEBSITE_CHANGE_KEY,
    ChangeRequest,
)
from common.dos import dos_location_cache

FILE_PATH = "application.event_processor.event_processor"


@fixture
def mock_metric_logger():
    InvocationTracker.reset()

    async def flush(self):
        print("flush called")
        InvocationTracker.record()

    MetricsLogger.flush = flush


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
            "OpeningTime": "08:45",
            "ClosingTime": "17:00",
            "OffsetOpeningTime": 525,
            "OffsetClosingTime": 1020,
            "OpeningTimeType": "General",
            "AdditionalOpeningDate": "",
            "IsOpen": True,
        },
        {
            "Weekday": "Friday",
            "OpeningTime": "08:45",
            "ClosingTime": "17:00",
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
        PUBLICNAME_CHANGE_KEY: nhs_entity.org_name,
        ADDRESS_CHANGE_KEY: {
            ADDRESS_LINES_KEY: nhs_entity.address_lines,
            POSTCODE_CHANGE_KEY: nhs_entity.postcode,
        },
    }
    assert cr.changes == expected_changes, f"Changes should be {expected_changes} but they are {cr.changes}"


@patch.object(Logger, "error")
def test_get_change_requests_when_no_matching_services(mock_logger):
    # Arrange
    nhs_entity = NHSEntity({})
    nhs_entity.odscode = "SLC45"
    nhs_entity.website = "www.site.com"
    nhs_entity.phone = "01462622435"
    nhs_entity.postcode = "S45 1AA"
    nhs_entity.org_name = "Fake NHS Service"
    nhs_entity.address_lines = ["Fake Street1", "Fake Street2", "Fake Street3", "Fake City", "Fake County"]
    nhs_entity.OpeningTimes = []

    event_processor = EventProcessor(nhs_entity)
    event_processor.matching_services = None
    # Act
    event_processor.get_change_requests()
    # Assert
    mock_logger.assert_called_with("Attempting to form change requests before matching services have been found.")


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


def get_message_attributes(
    correlation_id: str,
    message_received: int,
    record_id: str,
    ods_code: str,
    message_deduplication_id: str,
    message_group_id: str,
):
    return {
        "correlation_id": {"DataType": "String", "StringValue": correlation_id},
        "message_received": {"DataType": "Number", "StringValue": str(message_received)},
        "dynamo_record_id": {"DataType": "String", "StringValue": record_id},
        "ods_code": {"DataType": "String", "StringValue": ods_code},
        "message_deduplication_id": {"DataType": "String", "StringValue": message_deduplication_id},
        "message_group_id": {"DataType": "String", "StringValue": message_group_id},
    }


@patch.object(Logger, "get_correlation_id", return_value="1")
@patch.object(Logger, "info")
@patch(f"{FILE_PATH}.client")
def test_send_changes(mock_client, mock_logger, get_correlation_id_mock):
    # Arrange
    q_name = "test"
    environ["CR_QUEUE_URL"] = q_name
    change_request = ChangeRequest(service_id=49016)
    change_request.reference = "1"
    change_request.system = "Profile Updater (test)"
    change_request.message = "Test message 1531816592293|@./"
    change_request.changes = {
        PHONE_CHANGE_KEY: "0118 999 88199 9119 725 3",
        WEBSITE_CHANGE_KEY: "https://www.google.pl",
    }
    record_id = "someid"
    message_received = 1642501355616
    nhs_entity = NHSEntity({})
    nhs_entity.odscode = "SLC45"
    nhs_entity.website = "www.site.com"
    nhs_entity.phone = "01462622435"
    nhs_entity.postcode = "S45 1AA"
    nhs_entity.org_name = "Fake NHS Service"
    nhs_entity.address_lines = ["Fake Street1", "Fake Street2", "Fake Street3", "Fake City", "Fake County"]
    sequence_number = 1

    event_processor = EventProcessor(nhs_entity)
    event_processor.change_requests = [change_request]
    # Act
    event_processor.send_changes(message_received, record_id, sequence_number)
    # Assert
    mock_client.assert_called_with("sqs")
    change_payload = dumps(change_request.create_payload())
    encoded = change_payload.encode()
    hashed_payload = hashlib.sha256(encoded).hexdigest()
    entry_details = {
        "Id": "49016-1",
        "MessageBody": change_payload,
        "MessageDeduplicationId": f"1-{hashed_payload}",
        "MessageGroupId": "49016",
        "MessageAttributes": get_message_attributes(
            "1", message_received, record_id, nhs_entity.odscode, f"1-{hashed_payload}", "49016"
        ),
    }
    mock_client.return_value.send_message_batch.assert_called_with(
        QueueUrl=q_name,
        Entries=[entry_details],
    )
    mock_logger.assert_called_with(f"Sent off change payload for id={change_request.service_id}")
    # Clean up
    del environ["CR_QUEUE_URL"]


@patch.object(Logger, "error")
@patch(f"{FILE_PATH}.client")
def test_send_changes_when_get_change_requests_not_run(mock_client, mock_logger):
    # Arrange
    record_id = "someid"
    message_received = 1642501355616

    nhs_entity = NHSEntity({})
    nhs_entity.odscode = "SLC45"
    nhs_entity.website = "www.site.com"
    nhs_entity.phone = "01462622435"
    nhs_entity.postcode = "S45 1AA"
    nhs_entity.org_name = "Fake NHS Service"
    nhs_entity.address_lines = ["Fake Street1", "Fake Street2", "Fake Street3", "Fake City", "Fake County"]
    sequence_number = 1
    event_processor = EventProcessor(nhs_entity)
    event_processor.change_requests = None
    # Act
    event_processor.send_changes(message_received, record_id, sequence_number)
    # Assert
    mock_logger.assert_called_with("Attempting to send change requests before get_change_requests has been called.")


@patch.object(Logger, "info")
@patch(f"{FILE_PATH}.client")
def test_send_changes_when_no_change_requests(mock_client, mock_logger):
    # Arrange
    record_id = "someid"
    message_received = 1642501355616
    nhs_entity = NHSEntity({})

    nhs_entity.odscode = "SLC45"
    nhs_entity.website = "www.site.com"
    nhs_entity.phone = "01462622435"
    nhs_entity.postcode = "S45 1AA"
    nhs_entity.org_name = "Fake NHS Service"
    nhs_entity.address_lines = ["Fake Street1", "Fake Street2", "Fake Street3", "Fake City", "Fake County"]
    sequence_number = 1
    event_processor = EventProcessor(nhs_entity)
    event_processor.change_requests = []
    # Act
    event_processor.send_changes(message_received, record_id, sequence_number)
    # Assert
    mock_logger.assert_called_with("No changes identified")
    mock_client.assert_called_with("sqs")
    mock_client.return_value.send_message_batch.assert_not_called()


@patch(f"{FILE_PATH}.get_latest_sequence_id_for_a_given_odscode_from_dynamodb")
@patch(f"{FILE_PATH}.add_change_request_to_dynamodb")
@patch(f"{FILE_PATH}.EventProcessor")
@patch(f"{FILE_PATH}.NHSEntity")
@patch(f"{FILE_PATH}.extract_body")
@patch(f"{FILE_PATH}.time_ns", return_value=1642619746522500523)
@patch.object(MetricsLogger, "put_metric")
@patch.object(MetricsLogger, "set_dimensions")
def test_lambda_handler_unmatched_service(
    mock_set_dimension,
    mock_put_metric,
    mock_time,
    mock_extract_body,
    mock_nhs_entity,
    mock_event_processor,
    mock_add_change_request_to_dynamodb,
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb,
    change_event,
    lambda_context,
    mock_metric_logger,
):
    # Arrange
    mock_entity = NHSEntity(change_event)
    sqs_event = SQS_EVENT.copy()
    environ["ENV"] = "test"
    sqs_event["Records"][0]["body"] = dumps(change_event)
    mock_extract_body.return_value = change_event
    mock_nhs_entity.return_value = mock_entity
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
    mock_set_dimension.assert_called_once_with({"ENV": "test"})

    mock_put_metric.assert_called_with("QueueToProcessorLatency", 3000, "Milliseconds")
    # Clean up
    for env in EXPECTED_ENVIRONMENT_VARIABLES:
        del environ[env]


@patch(f"{FILE_PATH}.disconnect_dos_db")
@patch(f"{FILE_PATH}.log_unmatched_nhsuk_pharmacies")
@patch(f"{FILE_PATH}.get_latest_sequence_id_for_a_given_odscode_from_dynamodb")
@patch(f"{FILE_PATH}.add_change_request_to_dynamodb")
@patch(f"{FILE_PATH}.EventProcessor")
@patch(f"{FILE_PATH}.NHSEntity")
@patch(f"{FILE_PATH}.extract_body")
def test_lambda_handler_no_matching_dos_services(
    mock_extract_body,
    mock_nhs_entity,
    mock_event_processor,
    mock_add_change_request_to_dynamodb,
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb,
    mock_log_unmatched_nhsuk_pharmacies,
    mock_disconnect_dos_db,
    change_event,
    lambda_context,
):
    # Arrange
    mock_entity = NHSEntity(change_event)
    sqs_event = SQS_EVENT.copy()
    sqs_event["Records"][0]["body"] = dumps(change_event)
    mock_extract_body.return_value = change_event
    mock_nhs_entity.return_value = mock_entity
    mock_add_change_request_to_dynamodb.return_value = 1
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb.return_value = 0
    mock_event_processor.return_value.get_matching_services.return_value = []
    for env in EXPECTED_ENVIRONMENT_VARIABLES:
        environ[env] = "test"
    # Act
    lambda_handler(sqs_event, lambda_context)
    # Assert
    mock_log_unmatched_nhsuk_pharmacies.assert_called_once()
    mock_event_processor.get_change_requests.assert_not_called()
    mock_disconnect_dos_db.assert_called_once()
    mock_event_processor.send_changes.assert_not_called()

    # Clean up
    for env in EXPECTED_ENVIRONMENT_VARIABLES:
        del environ[env]


@patch(f"{FILE_PATH}.disconnect_dos_db")
@patch(f"{FILE_PATH}.report_closed_or_hidden_services")
@patch(f"{FILE_PATH}.get_latest_sequence_id_for_a_given_odscode_from_dynamodb")
@patch(f"{FILE_PATH}.add_change_request_to_dynamodb")
@patch(f"{FILE_PATH}.EventProcessor")
@patch(f"{FILE_PATH}.NHSEntity")
@patch(f"{FILE_PATH}.extract_body")
def test_lambda_handler_hidden_or_closed_pharmacies(
    mock_extract_body,
    mock_nhs_entity,
    mock_event_processor,
    mock_add_change_request_to_dynamodb,
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb,
    mock_report_closed_or_hidden_services,
    mock_disconnect_dos_db,
    change_event,
    lambda_context,
):
    # Arrange
    service = dummy_dos_service()
    service.id = 1
    service.uid = 101
    service.odscode = "SLC4501"
    service.web = "www.fakesite.com"
    service.publicphone = "01462622435"
    service.postcode = "S45 1AB"

    change_event["OrganisationStatus"] = "closed"
    mock_entity = NHSEntity(change_event)
    sqs_event = SQS_EVENT.copy()
    sqs_event["Records"][0]["body"] = dumps(change_event)
    mock_extract_body.return_value = change_event
    mock_nhs_entity.return_value = mock_entity
    mock_add_change_request_to_dynamodb.return_value = 1
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb.return_value = 0
    mock_event_processor.return_value.get_matching_services.return_value = [service]

    for env in EXPECTED_ENVIRONMENT_VARIABLES:
        environ[env] = "test"
    # Act
    lambda_handler(sqs_event, lambda_context)
    # Assert
    mock_report_closed_or_hidden_services.assert_called_once()
    mock_disconnect_dos_db.assert_called_once()
    mock_event_processor.get_change_requests.assert_not_called()
    mock_event_processor.send_changes.assert_not_called()
    # Clean up
    for env in EXPECTED_ENVIRONMENT_VARIABLES:
        del environ[env]


@patch(f"{FILE_PATH}.disconnect_dos_db")
@patch(f"{FILE_PATH}.log_invalid_open_times")
@patch(f"{FILE_PATH}.get_latest_sequence_id_for_a_given_odscode_from_dynamodb")
@patch(f"{FILE_PATH}.add_change_request_to_dynamodb")
@patch(f"{FILE_PATH}.EventProcessor")
@patch(f"{FILE_PATH}.NHSEntity")
@patch(f"{FILE_PATH}.extract_body")
def test_lambda_handler_invalid_open_times(
    mock_extract_body,
    mock_nhs_entity,
    mock_event_processor,
    mock_add_change_request_to_dynamodb,
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb,
    mock_log_invalid_open_times,
    mock_disconnect_dos_db,
    change_event,
    lambda_context,
):
    # Arrange
    service = dummy_dos_service()
    service.id = 1
    service.uid = 101
    service.odscode = "SLC4501"
    service.web = "www.fakesite.com"
    service.publicphone = "01462622435"
    service.postcode = "S45 1AB"

    change_event["OpeningTimes"] = [
        {
            "Weekday": "Monday",
            "OpeningTime": "09:00",
            "ClosingTime": "13:00",
            "OpeningTimeType": "General",
            "AdditionalOpeningDate": "",
            "IsOpen": True,
        },
        {
            "Weekday": "Monday",
            "OpeningTime": "12:00",
            "ClosingTime": "17:30",
            "OpeningTimeType": "General",
            "AdditionalOpeningDate": "",
            "IsOpen": True,
        },
    ]
    mock_entity = NHSEntity(change_event)
    sqs_event = SQS_EVENT.copy()
    sqs_event["Records"][0]["body"] = dumps(change_event)
    mock_extract_body.return_value = change_event
    mock_nhs_entity.return_value = mock_entity
    mock_add_change_request_to_dynamodb.return_value = 1
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb.return_value = 0
    mock_event_processor.return_value.get_matching_services.return_value = [service]

    for env in EXPECTED_ENVIRONMENT_VARIABLES:
        environ[env] = "test"
    # Act
    lambda_handler(sqs_event, lambda_context)
    # Assert
    mock_log_invalid_open_times.assert_called_once()
    mock_disconnect_dos_db.assert_called_once()
    mock_event_processor.get_change_requests.assert_not_called()
    mock_event_processor.send_changes.assert_not_called()
    # Clean up
    for env in EXPECTED_ENVIRONMENT_VARIABLES:
        del environ[env]


@patch(f"{FILE_PATH}.get_latest_sequence_id_for_a_given_odscode_from_dynamodb")
@patch(f"{FILE_PATH}.add_change_request_to_dynamodb")
@patch(f"{FILE_PATH}.EventProcessor")
@patch(f"{FILE_PATH}.NHSEntity")
@patch(f"{FILE_PATH}.extract_body")
def test_lambda_handler_should_throw_exception(
    mock_extract_body,
    mock_nhs_entity,
    mock_event_processor,
    mock_add_change_request_to_dynamodb,
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb,
    change_event,
    lambda_context,
    caplog
):
    # Arrange
    service = dummy_dos_service()
    service.id = 1
    service.uid = 101
    service.odscode = "SLC4501"
    service.web = "www.fakesite.com"
    service.publicphone = "01462622435"
    service.postcode = "S45 1AB"

    del change_event["OrganisationSubType"]
    mock_entity = NHSEntity(change_event)
    sqs_event = SQS_EVENT.copy()
    sqs_event["Records"][0]["body"] = dumps(change_event)
    mock_extract_body.return_value = change_event
    mock_nhs_entity.return_value = mock_entity
    mock_add_change_request_to_dynamodb.return_value = 1
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb.return_value = 0
    mock_event_processor.return_value.get_matching_services.return_value = [service]
    for env in EXPECTED_ENVIRONMENT_VARIABLES:
        environ[env] = "test"
    # Act
    with caplog.at_level(logging.ERROR):
        lambda_handler(sqs_event, lambda_context)
    assert "Validation Error" in caplog.text
    # Clean up
    for env in EXPECTED_ENVIRONMENT_VARIABLES:
        del environ[env]


def test_lambda_handler_should_throw_exception_if_event_records_len_not_eq_one(lambda_context):
    # Arrange
    sqs_event = SQS_EVENT.copy()
    sqs_event["Records"] = []
    for env in EXPECTED_ENVIRONMENT_VARIABLES:
        environ[env] = "test"

    with raises(Exception):
        lambda_handler(sqs_event, lambda_context)
    for env in EXPECTED_ENVIRONMENT_VARIABLES:
        del environ[env]


@patch.object(Logger, "error")
def test_lambda_handler_given_env_variable_should_exists_in_given_list(mock_logger, change_event, lambda_context):
    # Arrange
    sqs_event = SQS_EVENT.copy()
    sqs_event["Records"][0]["body"] = dumps(change_event)
    environ["dummy"] = "test"
    # Act
    lambda_handler(sqs_event, lambda_context)
    mock_logger.assert_called_with("Environmental variable DB_SERVER not present")
    del environ["dummy"]


@patch.object(Logger, "error")
@patch(f"{FILE_PATH}.add_change_request_to_dynamodb")
@patch(f"{FILE_PATH}.get_latest_sequence_id_for_a_given_odscode_from_dynamodb")
@patch(f"{FILE_PATH}.EventProcessor")
@patch(f"{FILE_PATH}.NHSEntity")
@patch(f"{FILE_PATH}.extract_body")
def test_lambda_handler_no_sequence_number(
    mock_extract_body,
    mock_nhs_entity,
    mock_event_processor,
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
    mock_add_change_request_to_dynamodb.return_value = None
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb.return_value = 0
    for env in EXPECTED_ENVIRONMENT_VARIABLES:
        environ[env] = "test"
    # Act
    response = lambda_handler(sqs_event, lambda_context)
    # Assert
    assert response is None, f"Response should be None but is {response}"
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
@patch(f"{FILE_PATH}.EventProcessor")
@patch(f"{FILE_PATH}.NHSEntity")
@patch(f"{FILE_PATH}.extract_body")
def test_lambda_handler_sequence_number_is_less_than_db_sequence_number(
    mock_extract_body,
    mock_nhs_entity,
    mock_event_processor,
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
    mock_add_change_request_to_dynamodb.return_value = None
    mock_get_sequence_number.return_value = 1
    mock_get_latest_sequence_id_for_a_given_odscode_from_dynamodb.return_value = 3
    for env in EXPECTED_ENVIRONMENT_VARIABLES:
        environ[env] = "test"
    # Act
    response = lambda_handler(sqs_event, lambda_context)
    # Assert
    assert response is None, f"Response should be None but is {response}"
    mock_nhs_entity.assert_not_called()
    mock_event_processor.assert_not_called()
    mock_event_processor.send_changes.assert_not_called()
    mock_logger.assert_called_with(
        "Sequence id is smaller than the existing one in db for a given odscode, so will be ignored",
        extra={"incoming_sequence_number": 1, "db_latest_sequence_number": 3},
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
                "SentTimestamp": "1642619743522",
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


class InvocationTracker(object):
    invocations = 0

    @staticmethod
    def record():
        InvocationTracker.invocations += 1

    @staticmethod
    def reset():
        InvocationTracker.invocations = 0
