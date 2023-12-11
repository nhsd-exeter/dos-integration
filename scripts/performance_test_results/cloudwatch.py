from datetime import datetime
from os import getenv

from boto3 import client

cloudwatch_client = client("cloudwatch")


def get_lambda_metric_data(
    metric_namespace: str,
    metric_name: str,
    lambda_name: str,
    start_time: datetime,
    end_time: datetime,
    statistic: str,
    unit: str,
) -> object:
    """Get metric data for a lambda function.

    Args:
        metric_namespace (str): Cloudwatch metric namespace
        metric_name (str): Cloudwatch metric name
        lambda_name (str): Lambda function name
        start_time (datetime): Start time for metrics query
        end_time (datetime): End time for metrics query
        statistic (str): Statistic to return
        unit (str): Unit for metric

    Returns:
        object: Cloudwatch metric response object, may include metric data
    """
    return cloudwatch_client.get_metric_data(
        MetricDataQueries=[
            {
                "Id": "m1",
                "MetricStat": {
                    "Metric": {
                        "Namespace": metric_namespace,
                        "MetricName": metric_name,
                        "Dimensions": [
                            {"Name": "FunctionName", "Value": lambda_name},
                        ],
                    },
                    "Period": 60,
                    "Stat": statistic,
                    "Unit": unit,
                },
                "ReturnData": True,
            },
        ],
        StartTime=start_time,
        EndTime=end_time,
    )


def get_database_metric_data(
    metric_namespace: str,
    metric_name: str,
    database_name: str,
    start_time: datetime,
    end_time: datetime,
    statistic: str,
    unit: str,
) -> str:
    """Get metric data for a database.

    Args:
        metric_namespace (str): Cloudwatch metric namespace
        metric_name (str): Cloudwatch metric name
        database_name (str): Database name
        start_time (datetime): Start time for metrics query
        end_time (datetime): End time for metrics query
        statistic (str): Statistic to return
        unit (str): Unit for metric

    Returns:
        str: Cloudwatch metric response object, may include metric data
    """
    return cloudwatch_client.get_metric_data(
        MetricDataQueries=[
            {
                "Id": "m2",
                "MetricStat": {
                    "Metric": {
                        "Namespace": metric_namespace,
                        "MetricName": metric_name,
                        "Dimensions": [
                            {"Name": "DBInstanceIdentifier", "Value": database_name},
                        ],
                    },
                    "Period": 60,
                    "Stat": statistic,
                    "Unit": unit,
                },
                "ReturnData": True,
            },
        ],
        StartTime=start_time,
        EndTime=end_time,
    )


def get_custom_metric_data(
    metric_namespace: str,
    metric_name: str,
    start_time: datetime,
    end_time: datetime,
    statistic: str,
) -> str:
    """Get metric data for a custom metric.

    Args:
        metric_namespace (str): Cloudwatch metric namespace
        metric_name (str): Cloudwatch metric name
        start_time (datetime): Start time for metrics query
        end_time (datetime): End time for metrics query
        statistic (str): Statistic to return

    Returns:
        str: Cloudwatch metric response object, may include metric data
    """
    return cloudwatch_client.get_metric_data(
        MetricDataQueries=[
            {
                "Id": "m3",
                "MetricStat": {
                    "Metric": {
                        "Namespace": metric_namespace,
                        "MetricName": metric_name,
                        "Dimensions": [
                            {"Name": "environment", "Value": getenv("ENVIRONMENT")},
                        ],
                    },
                    "Period": 60,
                    "Stat": statistic,
                },
                "ReturnData": True,
            },
        ],
        StartTime=start_time,
        EndTime=end_time,
    )
