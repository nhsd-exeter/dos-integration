from os import getenv

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.tracing import Tracer
from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent, event_source
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext

from .check_dos import (
    check_for_palliative_care_profiling,
    check_for_zcode_profiling_on_incorrect_type,
    check_pharmacy_profiling,
)
from common.commissioned_service_type import BLOOD_PRESSURE, CONTRACEPTION
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
        logger.info("Quality checker started")
        check_dos_data_quality()
        logger.warning(
            "Quality checker finished",
            environment=getenv("ENVIRONMENT"),
            cloudwatch_metric_filter_matching_attribute="QualityCheckerFinished",
        )
    except Exception:
        logger.exception(
            "Quality checker Errored",
            environment=getenv("ENVIRONMENT"),
            cloudwatch_metric_filter_matching_attribute="QualityCheckerErrored",
        )
        raise


def check_dos_data_quality() -> None:
    """Check the data quality of the dos database."""
    with connect_to_db_reader() as db_connection:
        # Checks matched odscode services for pharmacy profiling
        check_pharmacy_profiling(db_connection)

        # Checks matched odscode services for incorrectly profiled palliative care
        check_for_palliative_care_profiling(db_connection)

        # Checks matched odscode services for incorrectly profiled blood pressure
        check_for_zcode_profiling_on_incorrect_type(db_connection, BLOOD_PRESSURE)

        # Checks matched odscode services for incorrectly profiled contraception
        check_for_zcode_profiling_on_incorrect_type(db_connection, CONTRACEPTION)
