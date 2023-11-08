from datetime import datetime
from json import dumps
from os import getenv
from sqlite3 import Timestamp
from time import sleep

from boto3 import client
from botocore.exceptions import ClientError
from pytz import timezone

LAMBDA_CLIENT_LOGS = client("logs")


def get_logs(
    query: str,
    lambda_name: str,
    start_time: Timestamp | None = None,
    retry_count: int = 32,
    sleep_per_loop: int = 20,
) -> str:
    """Get logs from CloudWatch.

    Args:
        query (str): CloudWatch Logs Insights query
        lambda_name (str): Lambda logs to search
        start_time (Timestamp): Start time for the query
        retry_count (int, optional): Retries for the query. Defaults to 32.
        sleep_per_loop (int, optional): Sleep time between retries. Defaults to 20.

    Returns:
        str: CloudWatch Logs Insights query response
    """
    log_group_name = get_log_group_name(lambda_name)
    logs_found = False
    counter = 0
    while not logs_found:
        try:
            start_query_response = LAMBDA_CLIENT_LOGS.start_query(
                logGroupName=log_group_name,
                startTime=int(start_time),
                endTime=int(datetime.now(timezone("Europe/London")).timestamp()),
                queryString=query,
            )
        except ClientError as error:
            if error.response["Error"]["Code"] == "LimitExceededException":
                sleep(sleep_per_loop * 3)
                continue
            raise
        query_id = start_query_response["queryId"]
        response = None
        while response is None or response["status"] != "Complete":
            sleep(sleep_per_loop)
            response = LAMBDA_CLIENT_LOGS.get_query_results(queryId=query_id)
        counter += 1
        if response["results"] != []:
            logs_found = True
        elif counter == retry_count:
            print(f"Log search retries exceeded.. no logs found for query: {query}")
            msg = "Log search retries exceeded.. no logs found"
            raise ValueError(msg)
    return dumps(response, indent=2)


def negative_log_check(query: str, event_lambda: str, start_time: Timestamp) -> bool:
    """Check logs don't exist.

    Args:
        query (str): CloudWatch Logs Insights query
        event_lambda (str): Lambda logs to search
        start_time (Timestamp): Start time for the query

    Returns:
        bool: True if no logs found
    """
    log_group_name = get_log_group_name(event_lambda)
    logs_found = False
    while not logs_found:
        try:
            start_query_response = LAMBDA_CLIENT_LOGS.start_query(
                logGroupName=log_group_name,
                startTime=int(start_time),
                endTime=int(datetime.now(timezone("Europe/London")).timestamp()),
                queryString=query,
            )
        except ClientError as error:
            if error.response["Error"]["Code"] == "LimitExceededException":
                sleep(20)
                continue
            raise
        logs_found = True

    query_id = start_query_response["queryId"]
    sleep(30)
    response = LAMBDA_CLIENT_LOGS.get_query_results(queryId=query_id)

    if response["results"] == []:
        return True

    msg = "Matching logs have been found"
    raise ValueError(msg)


def get_log_group_name(lambda_name: str) -> str:
    """Get the log group name for a lambda.

    Args:
        lambda_name (str): Lambda name

    Returns:
        str: Log group name
    """
    return f'/aws/lambda/uec-dos-int-{getenv("BLUE_GREEN_ENVIRONMENT")}-{lambda_name}'
