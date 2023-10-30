from unittest.mock import MagicMock, call, patch

from application.quality_checker.check_dos import (
    check_for_multiple_of_service_type,
    check_for_zcode_profiling_on_incorrect_type,
    check_pharmacy_profiling,
)
from common.commissioned_service_type import BLOOD_PRESSURE, CONTRACEPTION

FILE_PATH = "application.quality_checker.check_dos"


@patch(f"{FILE_PATH}.check_for_multiple_of_service_type")
@patch(f"{FILE_PATH}.search_for_matching_services")
@patch(f"{FILE_PATH}.search_for_pharmacy_ods_codes")
def test_check_pharmacy_profiling(
    mock_search_for_pharmacy_ods_codes: MagicMock,
    mock_search_for_matching_services: MagicMock,
    mock_check_for_multiple_of_service_type: MagicMock,
) -> None:
    # Arrange
    connection = MagicMock()
    odscode = "ABC123"
    mock_search_for_pharmacy_ods_codes.return_value = [odscode]
    # Act
    check_pharmacy_profiling(connection)
    # Assert
    mock_search_for_pharmacy_ods_codes.assert_called_once_with(connection)
    mock_search_for_matching_services.assert_called_once_with(connection, odscode)
    mock_check_for_multiple_of_service_type.assert_has_calls(
        calls=[
            call(mock_search_for_matching_services.return_value, BLOOD_PRESSURE),
            call(mock_search_for_matching_services.return_value, CONTRACEPTION),
        ],
    )


@patch(f"{FILE_PATH}.log_to_quality_check_report")
@patch(f"{FILE_PATH}.search_for_incorrectly_profiled_z_code_on_incorrect_type")
def test_check_for_zcode_profiling_on_incorrect_type(
    mock_search_for_incorrectly_profiled_z_code_on_incorrect_type: MagicMock,
    mock_log_to_quality_check_report: MagicMock,
) -> None:
    # Arrange
    connection = MagicMock()
    service = MagicMock()
    matched_services = [service]
    mock_search_for_incorrectly_profiled_z_code_on_incorrect_type.return_value = matched_services
    # Act
    check_for_zcode_profiling_on_incorrect_type(connection, BLOOD_PRESSURE)
    # Assert
    mock_search_for_incorrectly_profiled_z_code_on_incorrect_type.assert_called_once_with(connection, BLOOD_PRESSURE)
    mock_log_to_quality_check_report.assert_called_once_with(
        matched_services,
        "Blood Pressure ZCode is on invalid service type",
        BLOOD_PRESSURE.DOS_SG_SD_ID,
    )


@patch(f"{FILE_PATH}.log_to_quality_check_report")
@patch(f"{FILE_PATH}.search_for_incorrectly_profiled_z_code_on_incorrect_type")
def test_check_for_zcode_profiling_on_incorrect_type_no_matches(
    mock_search_for_incorrectly_profiled_z_code_on_incorrect_type: MagicMock,
    mock_log_to_quality_check_report: MagicMock,
) -> None:
    # Arrange
    connection = MagicMock()
    matched_services = []
    mock_search_for_incorrectly_profiled_z_code_on_incorrect_type.return_value = matched_services
    # Act
    check_for_zcode_profiling_on_incorrect_type(connection, BLOOD_PRESSURE)
    # Assert
    mock_search_for_incorrectly_profiled_z_code_on_incorrect_type.assert_called_once_with(connection, BLOOD_PRESSURE)
    mock_log_to_quality_check_report.assert_not_called()


@patch(f"{FILE_PATH}.log_to_quality_check_report")
def test_check_for_multiple_of_service_type(mock_log_to_quality_check_report: MagicMock) -> None:
    # Arrange
    to_be_matched_services = [
        MagicMock(typeid=BLOOD_PRESSURE.DOS_TYPE_ID),
        MagicMock(typeid=BLOOD_PRESSURE.DOS_TYPE_ID),
    ]
    not_to_be_matched_services = [
        MagicMock(typeid=CONTRACEPTION.DOS_TYPE_ID),
    ]
    matched_services = to_be_matched_services + not_to_be_matched_services
    # Act
    check_for_multiple_of_service_type(matched_services, BLOOD_PRESSURE)
    # Assert
    mock_log_to_quality_check_report.assert_called_once_with(
        to_be_matched_services,
        "Multiple 'Pharmacy' type services found (type 148)",
    )


@patch(f"{FILE_PATH}.log_to_quality_check_report")
def test_check_for_multiple_of_service_type_no_matches(mock_log_to_quality_check_report: MagicMock) -> None:
    # Arrange
    not_to_be_matched_services = [
        MagicMock(typeid=CONTRACEPTION.DOS_TYPE_ID),
    ]
    # Act
    check_for_multiple_of_service_type(not_to_be_matched_services, BLOOD_PRESSURE)
    # Assert
    mock_log_to_quality_check_report.assert_not_called()
