from os import environ
from unittest.mock import MagicMock, patch

from aws_lambda_powertools.logging import Logger

from application.quality_checker.reporting import log_to_quality_check_report, quality_check_report_metric

FILE_PATH = "application.quality_checker.reporting"


@patch(f"{FILE_PATH}.quality_check_report_metric")
@patch.object(Logger, "warning")
def test_log_to_quality_check_report(mock_warning_logger: MagicMock, mock_quality_check_report_metric: MagicMock):
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
        extra={
            "report_key": "QUALITY_CHECK_REPORT_KEY",
            "dos_service_uid": dos_service.uid,
            "dos_service_odscode": dos_service.odscode,
            "dos_service_name": dos_service.name,
            "dos_service_type_name": dos_service.service_type_name,
            "dos_service_type_id": dos_service.typeid,
            "dos_region": dos_service.get_region(),
            "z-code": "",
            "reason": reason,
            "odscode": dos_service.odscode[:5],
        },
    )
    mock_quality_check_report_metric.assert_called_once()


def test_quality_check_report_metric():
    # Arrange
    environ["ENV"] = "ENV"
    # Act & Assert
    quality_check_report_metric()
    # Cleanup
    del environ["ENV"]
