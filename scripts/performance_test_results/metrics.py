from datetime import datetime

from cloudwatch import get_custom_metric_data, get_database_metric_data, get_lambda_metric_data

CUSTOM_METRIC_NAMESPACE = "uec-dos-int"


def lambda_metrics(lambda_name: str, start_time: datetime, end_time: datetime) -> None:
    """Get metrics for a lambda function.

    Args:
        lambda_name (str): Lambda function name
        start_time (datetime): Start time for metrics
        end_time (datetime): End time for metrics
    """
    average_duration(lambda_name, start_time, end_time)
    error_count(lambda_name, start_time, end_time)


def throughput_metrics(start_time: datetime, end_time: datetime) -> None:
    """Get throughput metrics from custom metrics.

    Args:
        start_time (datetime): Start time for metrics
        end_time (datetime): End time for metrics
    """
    response = get_custom_metric_data(CUSTOM_METRIC_NAMESPACE, "UpdateRequestSuccess", start_time, end_time, "Sum")
    total_services_reviewed_or_updated = int(sum(response["MetricDataResults"][0]["Values"]))
    total_per_second = total_services_reviewed_or_updated / (end_time - start_time).total_seconds()
    print(f"Services Updated/Reviewed (UpdateRequestSuccess): {total_services_reviewed_or_updated}")
    print(f"Average Services Updated/Reviewed per second: {total_per_second}")


def database_metrics(database_name: str, database_description: str, start_time: datetime, end_time: datetime) -> None:
    """Get metrics for a database.

    Args:
        database_name (str): Database name
        database_description (str): Database description
        start_time (datetime): Start time for metrics
        end_time (datetime): End time for metrics
    """
    db_cpu_utilization_response = get_database_metric_data(
        "AWS/RDS", "CPUUtilization", database_name, start_time, end_time, "Maximum", "Percent"
    )
    cpu_utilization = max(db_cpu_utilization_response["MetricDataResults"][0]["Values"])
    db_connections_response = get_database_metric_data(
        "AWS/RDS", "DatabaseConnections", database_name, start_time, end_time, "Maximum", "Count"
    )
    connections = int(max(db_connections_response["MetricDataResults"][0]["Values"]))
    print(f"{database_description} - CPU Utilisation: {cpu_utilization}")
    print(f"{database_description} - Connections: {connections}")


def average_duration(lambda_name: str, start_time: datetime, end_time: datetime) -> None:
    """Get average duration for a lambda function.

    Args:
        lambda_name (str): Lambda function name
        start_time (datetime): Start time for metrics
        end_time (datetime): End time for metrics
    """
    response = get_lambda_metric_data(
        "AWS/Lambda", "Duration", lambda_name, start_time, end_time, "Average", "Milliseconds"
    )
    short_lambda_name = "-".join(lambda_name.split("-")[4:])
    values = response["MetricDataResults"][0]["Values"]
    print(f"Average duration for {short_lambda_name} is {sum(values) / len(values)} ms")


def error_count(lambda_name: str, start_time: datetime, end_time: datetime) -> None:
    """Get error count for a lambda function.

    Args:
        lambda_name (str): Lambda function name
        start_time (datetime): Start time for metrics
        end_time (datetime): End time for metrics
    """
    response = get_lambda_metric_data("AWS/Lambda", "Errors", lambda_name, start_time, end_time, "Sum", "Count")
    short_lambda_name = "-".join(lambda_name.split("-")[4:])
    values = response["MetricDataResults"][0]["Values"]
    print(f"Error count for {short_lambda_name} is {int(sum(values))}")
