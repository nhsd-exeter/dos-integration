from dataclasses import dataclass
from json import dumps
from os import environ
from aws_lambda_powertools.utilities.data_classes import SNSEvent
from pytest import fixture, raises
from application.slack_messenger.slack_messenger import lambda_handler, send_msg_slack, get_message_for_cloudwatch_event
from unittest.mock import patch

FILE_PATH = "application.slack_messenger.slack_messenger"


@fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = "slack-messenger"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:slack-messenger"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()


LAMBDA_INVOKE_RESPONSE = {
    "Payload": "",
    "StatusCode": 202,
    "ResponseMetadata": {},
}
MESSAGE = {
    "AlarmName": "Matthew Test",
    "AlarmDescription": "Testing alarm for invalid postcodes",
    "AWSAccountId": "000000000000",
    "AlarmConfigurationUpdatedTimestamp": "2022-02-22T12:22:09.734+0000",
    "NewStateValue": "ALARM",
    "NewStateReason": "Some message",
    "StateChangeTime": "2022-03-04T11:38:59.002+0000",
    "Region": "EU (London)",
    "AlarmArn": "arn:aws:cloudwatch:eu-west-2:000000000000:alarm:Matthew Test",
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
                "Subject": 'ALARM: "Matthew Test" in EU (London)',
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
    message = {}
    environ["SLACK_WEBHOOK_URL"] = "www.someexamplethingy.com"
    # Act
    with raises(KeyError):
        send_msg_slack(message)


@patch(f"{FILE_PATH}.post")
def test_send_message(mock_post, lambda_context):

    message = {"text": "hello dave"}
    environ["SLACK_WEBHOOK_URL"] = "www.someexamplethingy.com"
    environ["SLACK_ALERT_CHANNEL"] = "channel5"
    # Act
    send_msg_slack(message)
    mock_post.assert_called_once_with(
        url="www.someexamplethingy.com",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        json={"text": "hello dave", "channel": "channel5", "icon_emoji": ""},
    )


def test_get_messsage_from_event():

    # Arrange
    sns_event_dict = SNS_EVENT.copy()
    sns_event = SNSEvent(sns_event_dict)
    # Act
    message = get_message_for_cloudwatch_event(sns_event)

    assert message == {
        "attachments": [
            {
                "color": "#e01e5a",
                "fields": [
                    {
                        "short": True,
                        "title": "Alarm Name",
                        "value": "Matthew Test",
                    },
                    {
                        "short": True,
                        "title": "Alarm State",
                        "value": "ALARM",
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
                ],
                "ts": 1646393939.038,
            },
        ],
        "blocks": [
            {
                "text": {
                    "text": ":rotating_light:  *<https://console.aws.amazon.com/cloudwatch/home?"
                    "region=eu-west-2#alarm:alarmFilter=ANY;name=Matthew%20Test|Matthew Test>*",
                    "type": "mrkdwn",
                },
                "type": "section",
            },
        ],
    }
