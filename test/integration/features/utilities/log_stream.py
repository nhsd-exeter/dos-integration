from datetime import datetime
from os import getenv as get_env
from time import sleep
from boto3 import client
# from features.utilities.utilities import event_request_start_time

lambda_client_logs = client("logs")
log_group_name_event_processor = get_env("LOG_GROUP_NAME_EVENT_PROCESSOR")
event_processor = get_env("EVENT_PROCESSOR")


def get_processor_log_stream_name() -> str:
    sleep(1)
    log_stream = lambda_client_logs.describe_log_streams(
        logGroupName=log_group_name_event_processor,
        orderBy="LastEventTime",
        descending=True,
    )
    return log_stream["logStreams"][0]["logStreamName"]

def get_data_logs(search_string: str) -> str:
    log_present = False
    start_time = datetime.now()
    while log_present is False:
        time_delta = datetime.now() - start_time
        event_log = lambda_client_logs.get_log_events(
            logGroupName=log_group_name_event_processor,
            logStreamName=get_processor_log_stream_name(),
        )
        for item in event_log["events"]:
            if search_string in item["message"]:
                return item["message"]
            elif "ERROR" in item["message"]:
                raise Exception("event_processor failed to process Change Event: {0}".format(item["message"]))
        sleep(3)
        print("Searching for log data... Time elapsed: " + str(time_delta.seconds) + " Seconds")
        if time_delta.total_seconds() >= 10:
            raise TimeoutError("Unable to find log data")

def get_logs() -> str:
    event_log = lambda_client_logs.get_log_events(
            logGroupName=log_group_name_event_processor,
            logStreamName=get_processor_log_stream_name(),
            startTime=event_request_start_time
            # endTime=int(datetime.now().timestamp()),
    )
    messages=[]
    inverse_event_log=event_log["events"]
    for item in inverse_event_log:
        messages.append(item["message"])
    return event_request_start_time


    # for item in event_log["events"]:
    #         if "CR" in item["message"]:
    #             return item["message"]
    #         elif "ERROR" in item["message"]:
    #             event_log["events"][-1]["message"]
                # return event_log["events"]
            # else:
                # event_log["events"][-1]["message"]
                # raise Exception("Unable to find log data")

# return event_log["events"][-1]["message"]
