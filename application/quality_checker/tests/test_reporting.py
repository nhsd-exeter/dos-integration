from unittest.mock import MagicMock, patch

from aws_lambda_powertools.logging import Logger

from application.quality_checker.reporting import log_to_quality_check_report

FILE_PATH = "application.quality_checker.reporting"


@patch.object(Logger, "warning")
def test_log_to_quality_check_report(mock_warning_logger: MagicMock) -> None:
    # Arrange
    dos_service = MagicMock()
    matched_services = [
        dos_service,
    ]
    reason = "reason"
    # Act
    log_to_quality_check_report(matched_services, reason)
    # Assert
    mock_warning_logger.assert_called_once_with(
        reason,
        report_key="QUALITY_CHECK_REPORT_KEY",
        dos_service_uid=dos_service.uid,
        dos_service_odscode=dos_service.odscode,
        dos_service_name=dos_service.name,
        dos_service_type_name=dos_service.service_type_name,
        dos_service_type_id=dos_service.typeid,
        dos_region=dos_service.get_region(),
        z_code="",
        reason=reason,
        odscode=dos_service.odscode[:5],
        environment="local",
        cloudwatch_metric_filter_matching_attribute="QualityCheckerIssueFound",
    )
