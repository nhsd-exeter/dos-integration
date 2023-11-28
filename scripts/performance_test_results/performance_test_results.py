from datetime import datetime
from os import getenv

from metrics import database_metrics, lambda_metrics, throughput_metrics


def performance_test_results() -> None:
    start_time = datetime(2023, 11, 28, 10, 0, 0, tzinfo=None)
    end_time = datetime(2023, 11, 28, 12, 0, 0, tzinfo=None)
    lambda_metrics(getenv("INGEST_CHANGE_EVENT_LAMBDA"), start_time, end_time)
    lambda_metrics(getenv("SERVICE_MATCHER_LAMBDA"), start_time, end_time)
    lambda_metrics(getenv("SERVICE_SYNC_LAMBDA"), start_time, end_time)
    throughput_metrics(start_time, end_time)
    database_metrics(getenv("DB_WRITER_NAME"), "Writer", start_time, end_time)
    database_metrics(getenv("DB_READER_NAME"), "Reader", start_time, end_time)


if __name__ == "__main__":
    performance_test_results()
