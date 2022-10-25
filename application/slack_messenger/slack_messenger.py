from datetime import datetime, timedelta
from json import loads
from os import environ
from typing import Any, Dict, TypedDict
from urllib.parse import quote

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.tracing import Tracer
from aws_lambda_powertools.utilities.data_classes import event_source, SNSEvent
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from requests import post

from common.constants import METRIC_REPORT_KEY_MAP
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
        f"{project_id}-service-matcher",
        f"{project_id}-service-sync",
        f"{project_id}-dos-db-update-dlq-handler",
        f"{project_id}-change-event-dlq-handler",
    ]
    filters = {"report_key": METRIC_REPORT_KEY_MAP.get(metric_name, "")}

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
    slack_message = {
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn", "text": f":rotating_light:  *<{link}|{alarm_name}>*"}}
        ],
        "attachments": [
            {
                "color": colour,
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
                        "value": f"<{generate_aws_cloudwatch_log_insights_url(region, log_groups, filters)}|View Logs>",
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


def generate_aws_cloudwatch_log_insights_url(region: str, log_groups: list, filters: dict, limit: int = 100):
    def quote_string(input_str):
        return f"""{quote(input_str, safe="~()'*").replace('%', '*')}"""

    def quote_list(input_list):
        quoted_list = ""
        for item in input_list:
            if isinstance(item, str):
                item = f"'{item}"
            quoted_list += f"~{item}"
        return f"({quoted_list})"

    params = []

    fields = "fields @timestamp,correlation_id,ods_code,level,message_received,function_name, message"
    query_filters = "\n".join([f'| filter {k}="{v}"' for (k, v) in filters.items()])
    query = f"{fields}\n{query_filters}\n| sort @timestamp asc\n| limit {limit}"

    parameters: TypedDict = {
        "end": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
        "start": (datetime.utcnow() - timedelta(hours=1)).isoformat(timespec="milliseconds") + "Z",
        "unit": "seconds",
        "timeType": "ABSOLUTE",  # "ABSOLUTE",  # OR RELATIVE and end = 0 and start is negative  seconds
        "tz": "Local",  # OR "UTC"
        "editorString": query,
        "isLiveTail": False,
        "source": [f"/aws/lambda/{lg}" for lg in log_groups],
    }

    for key, value in parameters.items():
        if key == "editorString":
            value = "'" + quote(value)
            value = value.replace("%", "*")
        elif isinstance(value, str):
            value = "'" + value
        if isinstance(value, bool):
            value = str(value).lower()
        elif isinstance(value, list):
            value = quote_list(value)
        params += [key, str(value)]

    object_string = quote_string("~(" + "~".join(params) + ")")
    scaped_object = quote(object_string, safe="*").replace("~", "%7E")
    with_query_detail = "?queryDetail=" + scaped_object
    result = quote(with_query_detail, safe="*").replace("%", "$")
    return f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:logs-insights{result}"


@unhandled_exception_logging()
@tracer.capture_lambda_handler()
@event_source(data_class=SNSEvent)
@logger.inject_lambda_context()
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
