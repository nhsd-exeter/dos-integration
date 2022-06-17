from datetime import datetime
from os import getenv as get_env
from sqlite3 import Timestamp
from time import sleep
from boto3 import client
from json import dumps

LAMBDA_CLIENT_LOGS = client("logs")
EVENT_PROCESSOR = get_env("EVENT_PROCESSOR")
EVENT_SENDER = get_env("EVENT_SENDER")
CR_FIFO_DLQ = get_env("CR_FIFO_DLQ")
LOG_GROUP_NAME_EVENT_PROCESSOR = f"/aws/lambda/{EVENT_PROCESSOR}"
LOG_GROUP_NAME_EVENT_SENDER = f"/aws/lambda/{EVENT_SENDER}"
LOG_GROUP_NAME_CR_FIFO_DLQ = f"/aws/lambda/{CR_FIFO_DLQ}"


def get_logs(
    query: str, event_lambda: str, start_time: Timestamp, retry_count: int = 32, sleep_per_loop: int = 20
) -> str:
    log_group_name = get_log_group_name(event_lambda)
    logs_found = False
    counter = 0
    while logs_found is False:
        start_query_response = LAMBDA_CLIENT_LOGS.start_query(
            logGroupName=log_group_name,
            startTime=int(start_time),
            endTime=int(datetime.now().timestamp()),
            queryString=query,
        )
        query_id = start_query_response["queryId"]
        response = None
        while response is None or response["status"] != "Complete":
            sleep(sleep_per_loop)
            response = LAMBDA_CLIENT_LOGS.get_query_results(queryId=query_id)
        counter += 1
        if response["results"] != []:
            logs_found = True
        elif counter == retry_count:
            raise ValueError("Log search retries exceeded.. no logs found")
    return dumps(response, indent=2)


def negative_log_check(query: str, event_lambda: str, start_time: Timestamp) -> str:
    log_group_name = get_log_group_name(event_lambda)
    start_query_response = LAMBDA_CLIENT_LOGS.start_query(
        logGroupName=log_group_name,
        startTime=int(start_time),
        endTime=int(datetime.now().timestamp()),
        queryString=query,
    )

    query_id = start_query_response["queryId"]
    sleep(30)
    response = LAMBDA_CLIENT_LOGS.get_query_results(queryId=query_id)

    if response["results"] == []:
        return True
    else:
        raise ValueError("Matching logs have been found")


def get_log_group_name(event_lambda: str) -> str:
    log_groups = {
        "processor": LOG_GROUP_NAME_EVENT_PROCESSOR,
        "sender": LOG_GROUP_NAME_EVENT_SENDER,
        "cr_dlq": LOG_GROUP_NAME_CR_FIFO_DLQ,
    }
    if event_lambda == "processor" or "sender" or "cr_dlq":
        log_group_name = log_groups[event_lambda]
    else:
        raise ValueError("Error.. log group name not correctly specified")
    return log_group_name


def get_secret(secret_name: str) -> str:
    secrets_manager = client(service_name="secretsmanager")
    get_secret_value_response = secrets_manager.get_secret_value(SecretId=secret_name)
    return get_secret_value_response["SecretString"]
