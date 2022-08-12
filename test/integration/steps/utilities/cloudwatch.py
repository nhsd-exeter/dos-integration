from datetime import datetime
from json import dumps
from os import getenv
from sqlite3 import Timestamp
from time import sleep

from boto3 import client

LAMBDA_CLIENT_LOGS = client("logs")


def get_logs(
    query: str, lambda_name: str, start_time: Timestamp, retry_count: int = 32, sleep_per_loop: int = 20
) -> str:
    log_group_name = get_log_group_name(lambda_name)
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


def get_log_group_name(lambda_name: str) -> str:
    return f'/aws/lambda/uec-dos-int-{getenv("ENVIRONMENT")}-{lambda_name}'
