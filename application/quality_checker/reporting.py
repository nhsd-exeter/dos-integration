from os import getenv

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
            report_key=QUALITY_CHECK_REPORT_KEY,
            dos_service_uid=service.uid,
            dos_service_odscode=service.odscode,
            dos_service_name=service.name,
            dos_service_type_name=service.service_type_name,
            dos_service_type_id=service.typeid,
            dos_region=service.get_region(),
            z_code=z_code,
            reason=reason,
            odscode=service.odscode[:5],
            environment=getenv("ENVIRONMENT"),
            cloudwatch_metric_filter_matching_attribute="QualityCheckerIssueFound",
        )
