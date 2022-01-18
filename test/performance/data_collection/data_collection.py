from os import getenv
from pandas import DataFrame
from aws import get_queue_details
from datetime import datetime


def data_collection():
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    write_sqs_results_to_csv(getenv("FIFO_QUEUE_NAME"), f"{now}_fifo_queue_details.csv")
    write_sqs_results_to_csv(getenv("FIFO_DLQ_NAME"), f"{now}_fifo_dlq_details.csv")


def write_sqs_results_to_csv(sqs_queue_name: str, csv_name: str) -> None:
    queue_details = get_queue_details(sqs_queue_name)["Attributes"]
    queue_details = DataFrame.from_dict(queue_details, orient="index", columns=["Attribute Name"])
    queue_details.to_csv(f"results/{csv_name}", index=True)


if __name__ == "__main__":
    data_collection()
