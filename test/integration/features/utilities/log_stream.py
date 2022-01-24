from datetime import datetime, timedelta
from os import getenv as get_env
from time import sleep
from boto3 import client
from json import dumps
import json
from json.decoder import JSONDecodeError

LAMBDA_CLIENT_LOGS = client("logs")
EVENT_PROCESSOR = get_env("EVENT_PROCESSOR")
EVENT_SENDER = get_env("EVENT_SENDER")
LOG_GROUP_NAME_EVENT_PROCESSOR = f"/aws/lambda/{EVENT_PROCESSOR}"
LOG_GROUP_NAME_EVENT_SENDER = f"/aws/lambda/{EVENT_SENDER}"


def get_processor_log_stream_name() -> str:
    log_stream = LAMBDA_CLIENT_LOGS.describe_log_streams(
        logGroupName=LOG_GROUP_NAME_EVENT_PROCESSOR,
        orderBy="LastEventTime",
        descending=True,
    )
    return log_stream["logStreams"][0]["logStreamName"]


def get_sender_log_stream_name() -> str:
    log_stream = LAMBDA_CLIENT_LOGS.describe_log_streams(
        logGroupName=LOG_GROUP_NAME_EVENT_SENDER,
        orderBy="LastEventTime",
        descending=True,
    )
    return log_stream["logStreams"][0]["logStreamName"]


def get_logs(query: str, event_lambda: str) -> str:
    log_groups = {"processor": LOG_GROUP_NAME_EVENT_PROCESSOR, "sender": LOG_GROUP_NAME_EVENT_SENDER}
    if event_lambda == "processor" or "sender":
        log_group_name = log_groups[event_lambda]
    else:
        raise Exception("Error.. log group name not correctly specified")
    logs_found = False
    counter = 0
    while logs_found is False:
        start_query_response = LAMBDA_CLIENT_LOGS.start_query(
            logGroupName=log_group_name,
            startTime=int((datetime.today() - timedelta(minutes=5)).timestamp()),
            endTime=int(datetime.now().timestamp()),
            queryString=query,
        )
        query_id = start_query_response["queryId"]
        response = None
        while response is None or response["status"] != "Complete":
            sleep(15)
            response = LAMBDA_CLIENT_LOGS.get_query_results(queryId=query_id)
        counter += 1
        if response["results"] != []:
            logs_found = True
        elif counter == 14:
            raise Exception("Log search retries exceeded.. no logs found")
    return dumps(response, indent=2)


def get_processor_logs_list_for_debug(seconds_ago: int = 0) -> list:

    """Work out timestamps"""
    now = datetime.utcnow()
    past = now - timedelta(seconds=seconds_ago)

    # Get log events
    event_log = LAMBDA_CLIENT_LOGS.get_log_events(
        logGroupName=LOG_GROUP_NAME_EVENT_PROCESSOR,
        logStreamName=get_processor_log_stream_name(),
        startTime=int(past.timestamp() * 1000),
        endTime=int(now.timestamp() * 1000),
    )
    # If a message is a JSON string, format the string before returning.
    messages = []
    for event in event_log["events"]:
        try:
            messages.append(json.dumps(json.loads(event["message"]), indent=2))
        except JSONDecodeError:
            messages.append(event["message"])

    return messages


def get_processor_logs_within_time_frame_for_debug(time_in_seconds: int = 0) -> dict:
    logs = get_processor_logs_list_for_debug(time_in_seconds)
    for m in logs:
        print(m)
        # values.append(m["message"])
