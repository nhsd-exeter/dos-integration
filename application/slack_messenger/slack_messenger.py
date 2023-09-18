from datetime import datetime
from json import loads
from os import environ
from typing import Any
from urllib.parse import quote

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.tracing import Tracer
from aws_lambda_powertools.utilities.data_classes import SNSEvent, event_source
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from requests import post

from common.middlewares import unhandled_exception_logging

logger = Logger()
tracer = Tracer()


@unhandled_exception_logging()
@tracer.capture_lambda_handler()
@event_source(data_class=SNSEvent)
@logger.inject_lambda_context(clear_state=True)
def lambda_handler(event: SNSEvent, _context: LambdaContext) -> None:
    """Entrypoint handler for the slack_messenger lambda.

    Args:
        event (SNSEvent): SNS event
        context (LambdaContext): Lambda function context object

    Event: The event payload

    Some code may need to be changed if the exact input format is changed.
    """
    message = get_message_for_cloudwatch_event(event)
    logger.info("Sending alert to slack.", extra={"slack_message": message})
    send_msg_slack(message)


def get_message_for_cloudwatch_event(event: SNSEvent) -> dict[str, Any]:
    """Get message for CloudWatch event.

    Args:
        event (SNSEvent): SNS event

    Returns:
        dict[str, Any]: Message for slack
    """
    # Get Event
    record = next(event.records)
    timestamp = datetime.strptime(record.sns.timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
    message = loads(record.sns.message)
    environment = environ["SHARED_ENVIRONMENT"]
    # Get Alarm Info
    region = record.event_subscription_arn.split(":")[3]
    alarm_name: str = message["AlarmName"]
    new_state = message.get("NewStateValue", "")
    alarm_description = message.get("AlarmDescription", "")
    link = (
        "https://console.aws.amazon.com/cloudwatch/home"
        f"?region={region}#alarm:alarmFilter=ANY;name={quote(alarm_name.encode('utf-8'))}"
    )
    cloudwatch_dashboard_link = (
        f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}"
        f"#dashboards/dashboard/uec-dos-int-{environment}-monitoring-dashboard"
    )
    splunk_dashboard_link = "https://nhsdigital.splunkcloud.com/en-GB/app/nhsd_uec_pu_all_sh_all_viz/dos_integration_test_monitoring__update_request_summary_dashboard"

    emoji = ":white_check_mark:" if new_state == "OK" else ":rotating_light:"
    logger.append_keys(alarm_name=alarm_name, alarm_description=alarm_description)
    short_name = alarm_name.split("|")[2]

    return {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} {short_name}",
                    "emoji": True,
                },
            },
        ],
        "attachments": [
            {
                "color": get_alarm_colour(new_state),
                "fields": [
                    {
                        "value": (
                            f"*Name*: <{link}|{alarm_name}> | *State*: {new_state.capitalize()}\n"
                            f"*Description*: {alarm_description}\n"
                            f"<{cloudwatch_dashboard_link}|CloudWatch Monitoring Dashboard> | "
                            f"<{splunk_dashboard_link}|Splunk Dashboard>"
                        ),
                        "short": False,
                    },
                ],
                "ts": timestamp,
            },
        ],
    }


def get_alarm_colour(new_state: str) -> str:
    """Get alarm colour.

    Args:
        new_state (str): New state of the alarm

    Returns:
        str: Color of the alarm
    """
    if new_state == "ALARM":
        return "#e01e5a"
    return "good" if new_state == "OK" else "warning"


def send_msg_slack(message: dict[str, Any]) -> None:
    """Send message to slack.

    Args:
        message (dict[str, Any]): Message to send to slack
    """
    url = environ["SLACK_WEBHOOK_URL"]
    channel = environ["SLACK_ALERT_CHANNEL"]
    headers: dict[str, str] = {"Content-Type": "application/json", "Accept": "application/json"}
    message["channel"] = channel
    resp = post(url=url, headers=headers, json=message, timeout=5)
    logger.info(
        "Message sent to slack",
        extra={"slack_message": message, "status_code": resp.status_code, "response": resp.text},
    )
