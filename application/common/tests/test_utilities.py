from json import loads
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord

from pytest import raises, fixture
from ..utilities import (
    extract_body,
    get_sequence_number,
    handle_sqs_msg_attributes,
)


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
                    "ERROR_MESSAGE": {
                        "stringValue": "ApiDestination returned HTTP status 400 with payload: Dummy",
                        "stringListValues": [],
                        "binaryListValues": [],
                        "dataType": "String",
                    },
                    "ERROR_CODE": {
                        "stringValue": "SDK_CLIENT_ERROR",
                        "stringListValues": [],
                        "binaryListValues": [],
                        "dataType": "String",
                    },
                    "RULE_ARN": {
                        "stringValue": "arn:aws:events:eu:0:rule/dummy-eventbridge-bus/dummy-change-request-rule",
                        "stringListValues": [],
                        "binaryListValues": [],
                        "dataType": "String",
                    },
                    "TARGET_ARN": {
                        "stringValue": "arn:aws:events:eu:0:api-destination/dummy-dos-api-gateway-api-destination/abc",
                        "stringListValues": [],
                        "binaryListValues": [],
                        "dataType": "String",
                    },
                },
                "md5OfBody": "e4e68fb7bd0e697a0ae8f1bb342846b3",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:eventbridge-dlq-queue",
                "awsRegion": "us-east-2",
            }
        ]
    }


def test_extract_body():
    # Arrange
    expected_change_event = '{"test": "test"}'
    # Act
    change_event = extract_body(expected_change_event)
    # Assert
    assert (
        loads(expected_change_event) == change_event
    ), f"Change event should be {loads(expected_change_event)} but is {change_event}"


def test_extract_body_exception():
    # Arrange
    expected_change_event = {"test": "test"}
    # Act & Assert
    with raises(Exception):
        extract_body(expected_change_event)


def test_get_sequence_number():
    # Arrange
    record = SQSRecord(SQS_EVENT["Records"][0])
    # Act
    sequence_number = get_sequence_number(record)
    # Assert
    assert sequence_number == int(SQS_EVENT["Records"][0]["messageAttributes"]["sequence-number"]["stringValue"])


def test_get_sequence_number_empty():
    # Arrange
    sqs_event = SQS_EVENT.copy()
    del sqs_event["Records"][0]["messageAttributes"]["sequence-number"]
    record = SQSRecord(sqs_event["Records"][0])
    # Act
    sequence_number = get_sequence_number(record)
    # Assert
    assert sequence_number is None


def test_handle_sqs_msg_attributes(dead_letter_message):
    msg_attributes = dead_letter_message["Records"][0]["messageAttributes"]

    attributes = handle_sqs_msg_attributes(msg_attributes=msg_attributes)
    assert attributes["error_msg"] == msg_attributes["ERROR_MESSAGE"]["stringValue"]
    assert attributes["error_msg_http_code"] == 400
    assert attributes["error_code"] == msg_attributes["ERROR_CODE"]["stringValue"]
    assert attributes["rule_arn"] == msg_attributes["RULE_ARN"]["stringValue"]
    assert attributes["target_arn"] == msg_attributes["TARGET_ARN"]["stringValue"]


SQS_EVENT = {
    "Records": [
        {
            "messageId": "1",
            "receiptHandle": "3",
            "body": "Test message.",
            "attributes": {},
            "messageAttributes": {
                "sequence-number": {"stringValue": "1", "dataType": "Number"},
            },
            "md5OfBody": "e4e68fb7bd0e697a0ae8f1bb342846b3",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:my-queue",
            "awsRegion": "us-east-2",
        }
    ]
}
