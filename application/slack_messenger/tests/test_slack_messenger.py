from json import dumps
from os import environ
from unittest.mock import patch

import pytest
from aws_lambda_powertools.utilities.data_classes import SNSEvent

from application.slack_messenger.slack_messenger import get_message_for_cloudwatch_event, lambda_handler, send_msg_slack

FILE_PATH = "application.slack_messenger.slack_messenger"


LAMBDA_INVOKE_RESPONSE = {
    "Payload": "",
    "StatusCode": 202,
    "ResponseMetadata": {},
}
MESSAGE = {
    "AlarmName": "uec-dos-int | test |Invalid Postcodes Test",
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
        "Namespace": "uec-dos-int",
        "StatisticType": "Statistic",
        "Statistic": "SUM",
        "Unit": None,
        "Dimensions": [{"value": "ds-259", "name": "ENV"}],
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
                "TopicArn": "arn:aws:sns:eu-west-2:000000000000:uec-dos-int-ds-259-topic-app-alerts-for-slack",
                "Subject": 'ALARM: "Invalid Postcodes Test" in EU (London)',
                "Message": dumps(MESSAGE),
                "Timestamp": "2022-03-04T11:38:59.038Z",
                "SignatureVersion": "1",
                "Signature": "CRqguuRDp5XxupA5a42M4j1s6aDDDSQC/KCdlBw4PA==",
                "SigningCertUrl": "https://sns.eu-west-2.amazonaws.com/SimpleNotificationService-dg.pem",
                "UnsubscribeUrl": "whocares",
                "MessageAttributes": {},
            },
        },
    ],
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
    with pytest.raises(KeyError):
        send_msg_slack(message)


def test_send_message_url_no_channel(lambda_context):
    # Arrange
    message = {}
    environ["SLACK_WEBHOOK_URL"] = WEBHOOK_URL
    # Act & Assert
    with pytest.raises(KeyError):
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
        json={"text": "hello dave", "channel": "channel5"},
        timeout=5,
    )
    # Clean Up
    del environ["SLACK_WEBHOOK_URL"]


@pytest.mark.parametrize(
    ("new_state_value", "colour", "emoji"),
    [
        ("ALARM", "#e01e5a", ":rotating_light:"),
        ("OK", "good", ":white_check_mark:"),
        ("INSUFFICIENT_DATA", "warning", ":rotating_light:"),
    ],
)
def test_get_message_from_event(new_state_value: str, colour: str, emoji: str):
    # Arrange
    environ["SHARED_ENVIRONMENT"] = "test"
    sns_event_dict = SNS_EVENT.copy()
    message = MESSAGE.copy()
    message["NewStateValue"] = new_state_value
    sns_event_dict["Records"][0]["Sns"]["Message"] = dumps(message)
    sns_event = SNSEvent(sns_event_dict)
    # Act
    message = get_message_for_cloudwatch_event(sns_event)
    # Assert
    assert message == {
        "attachments": [
            {
                "color": colour,
                "fields": [
                    {
                        "short": False,
                        "value": f"*Name*: <https://console.aws.amazon.com/cloudwatch/home?region=eu-west-2#alarm:alarmFilter=ANY;name=uec-dos-int%20%7C%20test%20%7CInvalid%20Postcodes%20Test|uec-dos-int | test |Invalid Postcodes Test> | *State*: {new_state_value.capitalize()}\n*Description*: Testing alarm for invalid postcodes\n<https://eu-west-2.console.aws.amazon.com/cloudwatch/home?region=eu-west-2#dashboards/dashboard/uec-dos-int-test-monitoring-dashboard|CloudWatch Monitoring Dashboard> | <https://nhsdigital.splunkcloud.com/en-GB/app/nhsd_uec_pu_all_sh_all_viz/dos_integration_test_monitoring__update_request_summary_dashboard|Splunk Dashboard>",  # noqa: E501
                    },
                ],
                "ts": 1646393939.038,
            },
        ],
        "blocks": [
            {
                "text": {"emoji": True, "text": f"{emoji} Invalid Postcodes Test", "type": "plain_text"},
                "type": "header",
            },
        ],
    }
    # Clean Up
    del environ["SHARED_ENVIRONMENT"]
