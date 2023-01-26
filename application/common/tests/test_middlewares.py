import logging

from aws_lambda_powertools.utilities.data_classes import SQSEvent
from botocore.exceptions import ClientError
from pytest import raises

from ..middlewares import redact_staff_key_from_event, unhandled_exception_logging, unhandled_exception_logging_hidden_event


def test_redact_staff_key_from_event():
    @redact_staff_key_from_event()
    def dummy_handler(event, context):
        return event

    # Arrange
    event = SQS_EVENT.copy()
    # Act
    dummy_handler(event, None)


def test_unhandled_exception_logging(caplog):
    @unhandled_exception_logging
    def client_error_func(event, context):
        raise ClientError({"Error": {"Code": "dummy_error", "Message": "dummy_message"}}, "op_name")

    @unhandled_exception_logging
    def regular_error_func(event, context):
        raise Exception("dummy exception message")

    with caplog.at_level(logging.ERROR):

        with raises(ClientError):
            client_error_func(None, None)
        assert "Boto3 Client Error - 'dummy_error': dummy_message" in caplog.text

        with raises(Exception):
            regular_error_func(None, None)
        assert "dummy_error" in caplog.text


def test_unhandled_exception_logging_no_error():
    @unhandled_exception_logging
    def dummy_handler(event, context):
        pass

    # Arrange
    event = SQS_EVENT.copy()

    # Act
    dummy_handler(event, None)


def test_unhandled_exception_logging_hidden_event(caplog):
    @unhandled_exception_logging_hidden_event
    def regular_error_func(event, context):
        raise Exception("dummy exception message")

    with caplog.at_level(logging.ERROR):

        with raises(Exception):
            regular_error_func(None, None)
        assert "dummy_error" not in caplog.text


def test_unhandled_exception_logging_hidden_event_no_error():
    @unhandled_exception_logging_hidden_event
    def dummy_handler(event, context):
        pass

    # Arrange
    event = SQSEvent(None)
    # Act
    dummy_handler(event, None)

SQS_EVENT_BODY = '''{"description": "Default valid schema payload","SearchKey": "X","ODSCode": "XX123",
    "OrganisationName": "Generic Pharmacy","OrganisationTypeId": "PHA","OrganisationType": "Pharmacy",
    "OrganisationSubType": "Community","OrganisationStatus": "Visible",
    "Address1": "22 STUB STREET","Address2": null,"Address3": null,"City": "TESTON","County": null,
    "Latitude": 53.3623793029785,"Longitude": -2.15734055519104,"Postcode": "ST1 0UB",
    "ParentOrganisation": {"ODSCode": "XOP", "OrganisationName": "TESTON Stub services"},
    "OpeningTimes": [
        {"Weekday": "Monday", "OpeningTime": "07:30","ClosingTime": "23:30", "OffsetOpeningTime": 540,
        "OffsetClosingTime": 780, "OpeningTimeType": "General", "AdditionalOpeningDate": "", "IsOpen": true},
        {"Weekday": "Tuesday","OpeningTime": "07:30","ClosingTime": "23:30","OffsetOpeningTime": 540,
        "OffsetClosingTime": 780,"OpeningTimeType": "General","AdditionalOpeningDate": "","IsOpen": true},
        {"Weekday": "wednesday","OpeningTime": "07:30","ClosingTime": "23:30","OffsetOpeningTime": 540,
        "OffsetClosingTime": 780,"OpeningTimeType": "General","AdditionalOpeningDate": "","IsOpen": true},
        {"Weekday": "Thursday","OpeningTime": "07:30","ClosingTime": "23:30","OffsetOpeningTime": 540,
        "OffsetClosingTime": 780,"OpeningTimeType": "General","AdditionalOpeningDate": "","IsOpen": true},
        {"Weekday": "Friday","OpeningTime": "07:30","ClosingTime": "23:30","OffsetOpeningTime": 540,
        "OffsetClosingTime": 780,"OpeningTimeType": "General","AdditionalOpeningDate": "","IsOpen": true},
        {"Weekday": "Saturday","OpeningTime": "07:32","ClosingTime": "23:00","OffsetOpeningTime": 540,
        "OffsetClosingTime": 780,"OpeningTimeType": "General","AdditionalOpeningDate": "","IsOpen": true},
        {"Weekday": "Sunday","OpeningTime": "10:00","ClosingTime": "17:00","OffsetOpeningTime": 540,
        "OffsetClosingTime": 780,"OpeningTimeType": "General","AdditionalOpeningDate": "","IsOpen": true},
        {"Weekday": "", "OpeningTime": "10:00", "ClosingTime": "17:00", "OffsetOpeningTime": 0, "OffsetClosingTime": 0,
        "OpeningTimeType": "Additional", "AdditionalOpeningDate": "Dec 26 2022", "IsOpen": true}
    ],
    "Contacts": [
        {"ContactType": "Primary", "ContactAvailabilityType": "Office hours", "ContactMethodType": "Website",
        "ContactValue": "http://www.test.co.uk/"},
        {"ContactType": "Primary", "ContactAvailabilityType": "Office hours", "ContactMethodType": "Email",
        "ContactValue": "pharmacy.test@test.fake"},
        {"ContactType": "Primary", "ContactAvailabilityType": "Office hours", "ContactMethodType": "Telephone",
        "ContactValue": "0123 456 7891 2345 678 9"}
    ],
    "Staff": [
        {"Title": "Mr", "GivenName": "Dave", "FamilyName": "Davies", "Role": "Stub", "Qualification": "Unit"},
        {"Title": "Mr", "GivenName": "Dummy", "FamilyName": "Stubb", "Role": "Tester", "Qualification": ""}
    ],
    "Facilities": [{"Id": 1, "Value": "No"},{"Id": 2,"Value": "Yes"}],
    "LastUpdatedDates": {"OpeningTimes": "2021-09-07T10:21:30+00:00", "Facilities": "2021-09-07T10:21:42+00:00",
    "Services": "2021-09-07T10:21:36+00:00","ContactDetails": "2017-10-23T14:06:46+00:00"}}'''

SQS_EVENT = {
    "Records": [
        {
            "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
            "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy0a...",
            "body": SQS_EVENT_BODY,
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
