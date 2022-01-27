from datetime import datetime
from os import getenv
from pandas import DataFrame
from boto3 import client


def get_queue_details_to_csv(queue_name: str, file_name: str) -> None:
    try:
        sqs = client("sqs")
        response = sqs.get_queue_attributes(
            QueueUrl=f'https://sqs.{getenv("AWS_REGION")}.amazonaws.com/{getenv("AWS_ACCOUNT_ID")}/{queue_name}',
            AttributeNames=["All"],
        )
        dataframe = DataFrame(response["Attributes"], index=[0])
        file_name = file_name.replace(".fifo", "_fifo")
        dataframe.to_csv(f"results/{file_name}", index=False)
    except Exception as e:
        print(f"Exception Occurred when getting SQS Results: {str(e)}")
    return response


def get_metric_data_to_csv(namespace: str, metric_name: str, dimensions: list, file_name) -> None:
    try:
        metrics = client("cloudwatch", region_name=getenv("AWS_REGION"))
        response = metrics.get_metric_statistics(
            Namespace=namespace,
            MetricName=metric_name,
            Dimensions=dimensions,
            StartTime=datetime.strptime(getenv("START_TIME"), ("%Y-%m-%d_%H-%M-%S")),
            EndTime=datetime.strptime(getenv("END_TIME"), ("%Y-%m-%d_%H-%M-%S")),
            Period=60,
            Statistics=["SampleCount", "Average", "Sum", "Minimum", "Maximum"],
        )
        if len(response["Datapoints"]) > 0:
            dataframe = DataFrame(response["Datapoints"])
            dataframe.sort_values("Timestamp", inplace=True)
            dataframe.to_csv(f"results/{file_name}", index=False)
        else:
            print(f'No metrics {metric_name} found')
    except Exception as e:
        print(f"Exception Occurred when getting metrics results: Metric={metric_name} Exception={str(e)}")
    return response
