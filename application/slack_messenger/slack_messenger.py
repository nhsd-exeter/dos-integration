from json import loads
from os import environ
from typing import Any, Dict
from requests import post
from urllib.parse import quote
from datetime import datetime
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import SNSEvent, event_source
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from common.constants import INVALID_POSTCODE_REPORT_ID, INVALID_OPEN_TIMES_REPORT_ID
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
    namespace = str(message["Trigger"]["Namespace"]).lower()
    filter_env = list(filter(lambda s: s["name"] == "ENV", message["Trigger"]["Dimensions"]))
    env = filter_env[0]["value"] if len(filter_env) > 0 else ""
    new_state = message["NewStateValue"]
    alarm_description = message["AlarmDescription"]
    trigger = message["Trigger"]
    project_id = f"{namespace}-{env}"
    log_groups = [
        f"{project_id}-event-processor",
        f"{project_id}-event-sender",
        f"{project_id}-cr-fifo-dlq-handler",
        f"{project_id}-fifo-dlq-handler",
    ]
    filters = {"report_key": get_report_key(metric_name)}
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
                    {
                        "title": "",
                        "value": f"<{generate_cloudwatch_url(region, log_groups, filters)}|View Logs>",
                    },
                ],
                "ts": timestamp,
            }
        ],
    }
    return slack_message


def get_report_key(metric_name):
    if metric_name == "InvalidPostcode":
        return INVALID_POSTCODE_REPORT_ID
    elif metric_name == "InvalidOpenTimes":
        return INVALID_OPEN_TIMES_REPORT_ID
    return ""


def send_msg_slack(message):
    url = environ["SLACK_WEBHOOK_URL"]
    channel = environ["SLACK_ALERT_CHANNEL"]
    headers: Dict[str, str] = {"Content-Type": "application/json", "Accept": "application/json"}

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


def generate_cloudwatch_url(region: str, log_groups: list, filters: dict, limit: int = 100):
    def escape(s):
        for c in s:
            if c.isalpha() or c.isdigit() or c in ["-", "."]:
                continue
            c_hex = "*{0:02x}".format(ord(c))
            s = s.replace(c, c_hex)
        return s

    def generate_log_insights_url(params):
        S1 = "$257E"
        S2 = "$2528"
        S3 = "$2527"
        S4 = "$2529"

        res = f"{S1}{S2}"
        for k in params:
            value = params[k]
            if isinstance(value, str):
                value = escape(value)
            elif isinstance(value, list):
                for i in range(len(value)):
                    value[i] = escape(value[i])
            prefix = S1 if list(params.items())[0][0] != k else ""
            suffix = f"{S1}{S3}"
            if isinstance(value, list):
                value = "".join([f"{S1}{S3}{n}" for n in value])
                suffix = f"{S1}{S2}"
            elif isinstance(value, int) or isinstance(value, bool):
                value = str(value).lower()
                suffix = S1
            res += f"{prefix}{k}{suffix}{value}"
        res += f"{S4}{S4}"
        QUERY = f"logsV2:logs-insights$3Ftab$3Dlogs$26queryDetail$3D{res}"
        return f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#{QUERY}"

    query = "\n".join([f'| filter {k}="{v}"' for (k, v) in filters.items()])
    fields = "fields @timestamp,correlation_id,ods_code,level,message_received,function_name, message"
    params = {
        "end": 0,
        "start": -60 * 60 * 1,  # - 1hr
        "unit": "seconds",
        "timeType": "RELATIVE",  # "ABSOLUTE",  # OR RELATIVE and end = 0 and start is negative  seconds
        "tz": "Local",  # OR "UTC"
        "editorString": f"{fields}\n{query}\n| sort @timestamp desc\n| limit {limit}",
        "isLiveTail": False,
        "source": [f"/aws/lambda/{lg}" for lg in log_groups],
    }
    return generate_log_insights_url(params)


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
    send_msg_slack(message)
