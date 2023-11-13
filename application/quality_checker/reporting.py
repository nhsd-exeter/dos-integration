from os import environ
from typing import Any

from aws_embedded_metrics import metric_scope
from aws_lambda_powertools.logging import Logger

from common.dos import DoSService

QUALITY_CHECK_REPORT_KEY = "QUALITY_CHECK_REPORT_KEY"

logger = Logger(child=True)


def log_to_quality_check_report(
    matched_services: list[DoSService],
    reason: str,
    z_code: str = "",
) -> None:
    """Log a service to the quality check report.

    Args:
        matched_services (list[DoSService]): The DoS service to report
        reason (str): The reason for the report
        z_code (str): The z-code for the report
    """
    for service in matched_services:
        logger.warning(
            reason,
            extra={
                "report_key": QUALITY_CHECK_REPORT_KEY,
                "dos_service_uid": service.uid,
                "dos_service_odscode": service.odscode,
                "dos_service_name": service.name,
                "dos_service_type_name": service.service_type_name,
                "dos_service_type_id": service.typeid,
                "dos_region": service.get_region(),
                "z-code": z_code,
                "reason": reason,
                "odscode": service.odscode[:5],
            },
        )
        quality_check_report_metric()


@metric_scope
def quality_check_report_metric(metrics: Any) -> None:  # noqa: ANN401
    """Send a metric to indicate that the quality checker has found an issue.

    Args:
        metrics (Metrics): CloudWatch embedded metrics object
    """
    metrics.set_namespace("UEC-DOS-INT")
    metrics.set_dimensions({"ENV": environ["ENV"]})
    metrics.set_property("level", "WARNING")
    metrics.put_metric("QualityCheckerIssueFound", 1, "Count")
