from dataclasses import dataclass
from json import dumps
from os import environ
from unittest.mock import patch

from aws_lambda_powertools.utilities.data_classes import SNSEvent
from pytest import fixture, mark, raises

from application.slack_messenger.slack_messenger import (
    generate_aws_cloudwatch_log_insights_url,
    get_message_for_cloudwatch_event,
    lambda_handler,
    send_msg_slack,
)

from common.constants import INVALID_POSTCODE_REPORT_ID, METRIC_REPORT_KEY_MAP

FILE_PATH = "application.slack_messenger.slack_messenger"


@fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        """Mock LambdaContext - All dummy values"""

        function_name: str = "slack-messenger"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:000000000:function:slack-messenger"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()


LAMBDA_INVOKE_RESPONSE = {
    "Payload": "",
    "StatusCode": 202,
    "ResponseMetadata": {},
}
MESSAGE = {
    "AlarmName": "Invalid Postcodes Test",
    "AlarmDescription": "Testing alarm for invalid postcodes",
    "AWSAccountId": "000000000000",
    "AlarmConfigurationUpdatedTimestamp": "2022-02-22T12:22:09.734+0000",
    "NewStateValue": "ALARM",
    "NewStateReason": "Some message",
    "StateChangeTime": "2022-03-04T11:38:59.002+0000",
    "Region": "EU (London)",
    "AlarmArn": "arn:aws:cloudwatch:eu-west-2:000000000000:alarm:Invalid Postcodes Test",
    "OldStateValue": "INSUFFICIENT_DATA",
    "Trigger": {
        "MetricName": "InvalidPostcode",
        "Namespace": "UEC-DOS-INT",
        "StatisticType": "Statistic",
        "Statistic": "SUM",
        "Unit": None,
        "Dimensions": [{"value": "di-259", "name": "ENV"}],
        "Period": 300,
        "EvaluationPeriods": 1,
        "DatapointsToAlarm": 1,
        "ComparisonOperator": "GreaterThanThreshold",
        "Threshold": 0.0,
        "TreatMissingData": "missing",
        "EvaluateLowSampleCountPercentile": "",
    },
}
SNS_EVENT = {
    "Records": [
        {
            "EventSource": "aws:sns",
            "EventVersion": "1.0",
            "EventSubscriptionArn": "arn:aws:sns:eu-west-2:000000000000:bla:8d8be687-b919-4fe1-8a53-b7c3cd40bfd7",
            "Sns": {
                "Type": "Notification",
                "MessageId": "be6ed8fb-6ca6-5ecb-ba78-82609035c3ad",
                "TopicArn": "arn:aws:sns:eu-west-2:000000000000:uec-dos-int-di-259-topic-app-alerts-for-slack",
                "Subject": 'ALARM: "Invalid Postcodes Test" in EU (London)',
                "Message": dumps(MESSAGE),
                "Timestamp": "2022-03-04T11:38:59.038Z",
                "SignatureVersion": "1",
                "Signature": "CRqguuRDp5XxupA5a42M4j1s6aDDDSQC/KCdlBw4PA==",
                "SigningCertUrl": "https://sns.eu-west-2.amazonaws.com/SimpleNotificationService-dg.pem",
                "UnsubscribeUrl": "whocares",
                "MessageAttributes": {},
            },
        }
    ]
}

WEBHOOK_URL = "https://hooks.slack.com/services/1/2/3"


@patch(f"{FILE_PATH}.get_message_for_cloudwatch_event")
@patch(f"{FILE_PATH}.send_msg_slack")
def test_lambda_handler_slack_messenger(mock_send, mock_get, lambda_context):
    expected = {"somefield": "somevalue"}
    mock_send.return_value = None
    mock_get.return_value = expected
    # Arrange
    sns_event_dict = SNS_EVENT.copy()
    sns_event = SNSEvent(sns_event_dict)
    # Act
    lambda_handler(sns_event_dict, lambda_context)
    # Assert
    mock_get.assert_called_once_with(sns_event)
    mock_send.assert_called_once_with(expected)


def test_send_message_missing_url(lambda_context):
    message = {}
    # Act
    with raises(KeyError):
        send_msg_slack(message)


def test_send_message_url_no_channel(lambda_context):
    # Arrange
    message = {}
    environ["SLACK_WEBHOOK_URL"] = WEBHOOK_URL
    # Act & Assert
    with raises(KeyError):
        send_msg_slack(message)
    # Clean Up
    del environ["SLACK_WEBHOOK_URL"]


@patch(f"{FILE_PATH}.post")
def test_send_message(mock_post, lambda_context):
    # Arrange
    message = {"text": "hello dave"}
    environ["SLACK_WEBHOOK_URL"] = WEBHOOK_URL
    environ["SLACK_ALERT_CHANNEL"] = "channel5"
    # Act
    send_msg_slack(message)
    # Assert
    mock_post.assert_called_once_with(
        url=WEBHOOK_URL,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        json={"text": "hello dave", "channel": "channel5", "icon_emoji": ""},
    )
    # Clean Up
    del environ["SLACK_WEBHOOK_URL"]


@mark.parametrize("new_state_value, colour", (("ALARM", "#e01e5a"), ("OK", "good"), ("INSUFFICIENT_DATA", "warning")))
@patch(f"{FILE_PATH}.generate_aws_cloudwatch_log_insights_url")
def test_get_message_from_event(mock_cloudwatch_url, new_state_value, colour):
    # Arrange
    sns_event_dict = SNS_EVENT.copy()
    message = MESSAGE.copy()
    message["NewStateValue"] = new_state_value
    sns_event_dict["Records"][0]["Sns"]["Message"] = dumps(message)
    sns_event = SNSEvent(sns_event_dict)
    mock_cloudwatch_url.return_value = "https://test.com"
    # Act
    message = get_message_for_cloudwatch_event(sns_event)
    # Assert
    assert message == {
        "attachments": [
            {
                "color": colour,
                "fields": [
                    {
                        "short": True,
                        "title": "Alarm Name",
                        "value": "Invalid Postcodes Test",
                    },
                    {
                        "short": True,
                        "title": "Alarm State",
                        "value": new_state_value,
                    },
                    {
                        "short": False,
                        "title": "Alarm Description",
                        "value": "Testing alarm for invalid postcodes",
                    },
                    {
                        "short": False,
                        "title": "Trigger",
                        "value": "SUM InvalidPostcode GreaterThanThreshold 0.0 for 1 period(s)  of 300 seconds.",
                    },
                    {"title": "", "value": "<https://test.com|View Logs>"},
                ],
                "ts": 1646393939.038,
            },
        ],
        "blocks": [
            {
                "text": {
                    "text": ":rotating_light:  *<https://console.aws.amazon.com/cloudwatch/home?"
                    "region=eu-west-2#alarm:alarmFilter=ANY;name=Invalid%20Postcodes%20Test|Invalid Postcodes Test>*",
                    "type": "mrkdwn",
                },
                "type": "section",
            },
        ],
    }
    mock_cloudwatch_url.assert_called_once()


def test_generate_cloudwatch_url():
    # Arrange
    project_id = "test-service-name"
    region = "eu-west-2"
    metric_name = "InvalidPostcode"
    report_key = METRIC_REPORT_KEY_MAP.get(metric_name, "")
    log_groups = [f"{project_id}-service-matcher"]
    filters = {"report_key": report_key}
    expected_url = "https://eu-west-2.console.aws.amazon.com/cloudwatch/home?region=eu-west-2#logsV2"
    # Act
    url = generate_aws_cloudwatch_log_insights_url(region, log_groups, filters, 10)
    # Assert
    assert report_key == INVALID_POSTCODE_REPORT_ID
    assert log_groups == ["test-service-name-service-matcher"]
    assert url.startswith(expected_url)
