from os import environ
from typing import Any

from aws_embedded_metrics import metric_scope
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.tracing import Tracer
from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent, event_source
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext

from .check_dos import check_incorrect_zcode_profiling, check_pharmacy_profiling
from common.commissioned_service_type import BLOOD_PRESSURE, CONTRACEPTION, PALLIATIVE_CARE
from common.dos_db_connection import connect_to_db_reader
from common.middlewares import unhandled_exception_logging

logger = Logger()
tracer = Tracer()


@tracer.capture_lambda_handler()
@logger.inject_lambda_context(clear_state=True)
@unhandled_exception_logging
@event_source(data_class=EventBridgeEvent)
def lambda_handler(event: EventBridgeEvent, context: LambdaContext) -> None:  # noqa: ARG001
    """Lambda handler for quality checker."""
    try:
        logger.debug("Quality checker started.")
        check_dos_data_quality()
        logger.debug("Quality checker finished.")
        send_finished_metric()
    except Exception:
        send_errored_metric()
        raise


def check_dos_data_quality() -> None:
    """Check the data quality of the dos database."""
    with connect_to_db_reader() as db_connection:
        # Checks matched odscode services for pharmacy profiling
        check_pharmacy_profiling(db_connection)

        # Checks matched odscode services for incorrectly profiled palliative care
        check_incorrect_zcode_profiling(db_connection, PALLIATIVE_CARE)

        # Checks matched odscode services for incorrectly profiled blood pressure
        check_incorrect_zcode_profiling(db_connection, BLOOD_PRESSURE)

        # Checks matched odscode services for incorrectly profiled contraception
        check_incorrect_zcode_profiling(db_connection, CONTRACEPTION)


@metric_scope
def send_finished_metric(metrics: Any) -> None:  # noqa: ANN401
    """Send a metric to indicate that the quality checker has finished.

    Args:
        metrics (Metrics): CloudWatch embedded metrics object
    """
    metrics.set_namespace("UEC-DOS-INT")
    metrics.set_dimensions({"ENV": environ["ENV"]})
    metrics.put_metric("QualityCheckerFinished", 1, "Count")


@metric_scope
def send_errored_metric(metrics: Any) -> None:  # noqa: ANN401
    """Send a metric to indicate that the quality checker has errored.

    Args:
        metrics (Metrics): CloudWatch embedded metrics object
    """
    metrics.set_namespace("UEC-DOS-INT")
    metrics.set_dimensions({"ENV": environ["ENV"]})
    metrics.put_metric("QualityCheckerErrored", 1, "Count")
