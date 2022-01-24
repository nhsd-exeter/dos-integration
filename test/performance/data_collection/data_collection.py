from datetime import datetime
from os import getenv

from aws import get_metric_data_to_csv, get_queue_details_to_csv

CUSTOM_DIMENSIONS = [
    {"Name": "ServiceName", "Value": getenv("EVENT_SENDER_NAME")},
    {"Name": "LogGroup", "Value": getenv("EVENT_SENDER_NAME")},
    {"Name": "ServiceType", "Value": "AWS::Lambda::Function"},
    {"Name": "ENV", "Value": getenv("ENVIRONMENT")},
]


def data_collection():
    now = getenv("START_TIME")
    get_queue_details_to_csv(
        queue_name=getenv("FIFO_QUEUE_NAME"),
        file_name=f"{now}_{getenv('FIFO_QUEUE_NAME')}_details.csv",
    )
    get_queue_details_to_csv(
        queue_name=getenv("FIFO_DLQ_NAME"),
        file_name=f"{now}_{getenv('FIFO_DLQ_NAME')}_details.csv",
    )
    get_metric_data_to_csv(
        namespace="AWS/RDS",
        metric_name="DatabaseConnections",
        dimensions=[{"Name": "DBInstanceIdentifier", "Value": "uec-core-dos-regression-db-12-replica-di"}],
        file_name=f"{now}_db_connections.csv",
    )
    get_metric_data_to_csv(
        namespace="UEC-DOS-INT",
        metric_name="ProcessingLatency",
        dimensions=CUSTOM_DIMENSIONS,
        file_name=f"{now}_processing_latency.csv",
    )
    get_metric_data_to_csv(
        namespace="UEC-DOS-INT",
        metric_name="DosApiLayency",
        dimensions=CUSTOM_DIMENSIONS,
        file_name=f"{now}_dos_api_latency.csv",
    )
    # get_metric_data_to_csv(
    #     namespace="UEC-DOS-INT",
    #     metric_name="DoSApiFail",
    #     dimensions=CUSTOM_DIMENSIONS,
    #     file_name=f"{now}_dos_api_fail.csv",
    # )
    get_metric_data_to_csv(
        namespace="AWS/Lambda",
        metric_name="ConcurrentExecutions",
        dimensions=[
            {"Name": "FunctionName", "Value": getenv("EVENT_PROCESSOR_NAME")},
        ],
        file_name=f'{now}_{getenv("EVENT_PROCESSOR_NAME")}_concurrent_executions.csv',
    )
    get_metric_data_to_csv(
        namespace="AWS/Lambda",
        metric_name="Invocations",
        dimensions=[
            {"Name": "FunctionName", "Value": getenv("EVENT_PROCESSOR_NAME")},
        ],
        file_name=f'{now}_{getenv("EVENT_PROCESSOR_NAME")}_invocations.csv',
    )


if __name__ == "__main__":
    data_collection()
