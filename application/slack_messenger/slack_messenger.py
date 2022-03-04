from json import loads
from os import environ
from typing import Any, Dict
from requests import post
from urllib.parse import quote
from datetime import datetime
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import SNSEvent, event_source
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext

from common.middlewares import unhandled_exception_logging

logger = Logger()
tracer = Tracer()


def get_message_for_cloudwatch_event(event: SNSEvent) -> Dict[str, Any]:

    record = next(event.records)
    timestamp = datetime.strptime(record.sns.timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
    message = loads(record.sns.message)
    region = record.event_subscription_arn.split(":")[3]
    alarm_name: str = message["AlarmName"]

    metric_name = message["Trigger"]["MetricName"]
    new_state = message["NewStateValue"]
    alarm_description = message["AlarmDescription"]
    trigger = message["Trigger"]
    color = "warning"

    if message["NewStateValue"] == "ALARM":
        color = "#e01e5a"
    elif message["NewStateValue"] == "OK":
        color = "good"
    link = (
        "https://console.aws.amazon.com/cloudwatch/home"
        f"?region={region}#alarm:alarmFilter=ANY;name={quote(alarm_name.encode('utf-8'))}"
    )
    slack_message = {
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn", "text": f":rotating_light:  *<{link}|{alarm_name}>*"}}
        ],
        "attachments": [
            {
                "color": color,
                "fields": [
                    {"title": "Alarm Name", "value": alarm_name, "short": True},
                    {"title": "Alarm State", "value": new_state, "short": True},
                    {"title": "Alarm Description", "value": alarm_description, "short": False},
                    {
                        "title": "Trigger",
                        "value": f"{trigger['Statistic']} {metric_name} {trigger['ComparisonOperator']} "
                        f"{str(trigger['Threshold'])} for {str(trigger['EvaluationPeriods'])} period(s) "
                        f" of {str(trigger['Period'])} seconds.",
                        "short": False,
                    },
                ],
                "ts": timestamp,
            }
        ],
    }
    return slack_message


def send_msg_slack(message):
    url = environ["SLACK_WEBHOOK_URL"]
    channel = environ["SLACK_ALERT_CHANNEL"]
    headers: Dict[str, str] = {"Content-Type": "application/json", "Accept": "application/json"}
    if url is None:
        print("unable to send slack message, slack url not set")
    else:
        message["channel"] = channel
        message["icon_emoji"] = ""

        resp = post(
            url=url,
            headers=headers,
            json=message,
        )
        logger.info(
            "Message sent to slack",
            extra={"slack_message": message, "status_code": resp.status_code, "response": resp.text},
        )


@unhandled_exception_logging()
@tracer.capture_lambda_handler()
@event_source(data_class=SNSEvent)
@logger.inject_lambda_context
def lambda_handler(event: SNSEvent, context: LambdaContext) -> None:
    """Entrypoint handler for the slack_messenger lambda

    Args:
        event (SNSEvent):
        context (LambdaContext): Lambda function context object

    Event: The event payload

    Some code may need to be changed if the exact input format is changed.
    """

    message = get_message_for_cloudwatch_event(event)
    logger.info("Sending alert to slack.", extra={"slack_message": message})
    send_msg_slack(message=message)
