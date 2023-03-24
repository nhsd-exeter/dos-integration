from datetime import datetime
from json import loads
from os import environ
from typing import Any, Dict, List
from urllib.parse import quote

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.tracing import Tracer
from aws_lambda_powertools.utilities.data_classes import event_source, SNSEvent
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from requests import post

from common.middlewares import unhandled_exception_logging

logger = Logger()
tracer = Tracer()


def get_message_for_cloudwatch_event(event: SNSEvent) -> Dict[str, Any]:
    def is_expression_alarm() -> bool:
        logger.debug(
            "Checking if alarm is an expression alarm",
            extra={
                "alarm_name": alarm_name,
                "trigger": trigger,
                "expression": "Expression" in str(trigger),
            },
        )
        return "Expression" in str(trigger)

    def get_attachments_fields() -> List[Dict[str, Any]]:
        fields = [
            {
                "title": "Alarm Name",
                "value": alarm_name,
                "short": True,
            },
            {
                "title": "Alarm State",
                "value": new_state,
                "short": True,
            },
            {
                "title": "Alarm Description",
                "value": alarm_description,
                "short": False,
            },
        ]
        if not is_expression_alarm():
            logger.append_keys(metric_name=metric_name)
            fields.append(
                {
                    "title": "Trigger",
                    "value": f"{trigger['Statistic']} {metric_name} {trigger['ComparisonOperator']} "
                    f"{str(trigger['Threshold'])} for {str(trigger['EvaluationPeriods'])} period(s) "
                    f" of {str(trigger['Period'])} seconds.",
                    "short": False,
                }
            )
        return fields

    record = next(event.records)
    timestamp = datetime.strptime(record.sns.timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
    message = loads(record.sns.message)
    region = record.event_subscription_arn.split(":")[3]
    alarm_name: str = message["AlarmName"]

    trigger = message.get("Trigger", "")
    metric_name = trigger.get("MetricName", "")
    new_state = message.get("NewStateValue", "")
    alarm_description = message.get("AlarmDescription", "")

    logger.append_keys(alarm_name=alarm_name, alarm_description=alarm_description)

    if new_state == "ALARM":
        colour = "#e01e5a"
    elif new_state == "OK":
        colour = "good"
    else:
        colour = "warning"
    link = (
        "https://console.aws.amazon.com/cloudwatch/home"
        f"?region={region}#alarm:alarmFilter=ANY;name={quote(alarm_name.encode('utf-8'))}"
    )
    return {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":rotating_light:  *<{link}|{alarm_name}>*",
                },
            }
        ],
        "attachments": [
            {
                "color": colour,
                "fields": get_attachments_fields(),
                "ts": timestamp,
            }
        ],
    }


def send_msg_slack(message: Dict[str, Any]) -> None:
    url = environ["SLACK_WEBHOOK_URL"]
    channel = environ["SLACK_ALERT_CHANNEL"]
    headers: Dict[str, str] = {"Content-Type": "application/json", "Accept": "application/json"}

    message["channel"] = channel
    message["icon_emoji"] = ""

    resp = post(
        url=url,
        headers=headers,
        json=message,
        timeout=5,
    )
    logger.info(
        "Message sent to slack",
        extra={"slack_message": message, "status_code": resp.status_code, "response": resp.text},
    )


@unhandled_exception_logging()
@tracer.capture_lambda_handler()
@event_source(data_class=SNSEvent)
@logger.inject_lambda_context(clear_state=True)
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
    send_msg_slack(message)
