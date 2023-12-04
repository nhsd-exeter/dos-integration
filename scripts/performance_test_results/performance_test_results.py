from datetime import datetime
from os import getenv

from metrics import database_metrics, lambda_metrics, throughput_metrics


def performance_test_results() -> None:
    """Get performance test results."""
    start_time = datetime.fromisoformat(getenv("START_TIME"))
    end_time = datetime.fromisoformat(getenv("END_TIME"))
    lambda_metrics(getenv("INGEST_CHANGE_EVENT_LAMBDA"), start_time, end_time)
    lambda_metrics(getenv("SERVICE_MATCHER_LAMBDA"), start_time, end_time)
    lambda_metrics(getenv("SERVICE_SYNC_LAMBDA"), start_time, end_time)
    throughput_metrics(start_time, end_time)
    database_metrics(getenv("DB_WRITER_NAME"), "Writer", start_time, end_time)
    database_metrics(getenv("DB_READER_NAME"), "Reader", start_time, end_time)


if __name__ == "__main__":
    performance_test_results()
