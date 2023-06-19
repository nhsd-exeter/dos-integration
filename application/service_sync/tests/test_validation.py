from unittest.mock import MagicMock, patch

import pytest
from aws_lambda_powertools.logging import Logger

from application.common.nhs import NHSEntity
from application.service_sync.validation import validate_opening_times, validate_website

FILE_PATH = "application.service_sync.validation"


@patch(f"{FILE_PATH}.log_service_with_generic_bank_holiday")
@patch.object(Logger, "warning")
def test_validate_opening_times_sucessful(
    mock_warning_logger: MagicMock,
    mock_log_service_with_generic_bank_holiday: MagicMock,
):
    # Arrange
    nhs_entity = MagicMock()
    nhs_entity.odscode.return_value = "12345"
    nhs_entity.all_times_valid.return_value = True
    dos_service = MagicMock()
    dos_service.any_generic_bankholiday_open_periods.return_value = False
    # Act
    result = validate_opening_times(dos_service, nhs_entity)
    # Assert
    assert result is True
    mock_warning_logger.assert_not_called()
    mock_log_service_with_generic_bank_holiday.assert_not_called()


@patch(f"{FILE_PATH}.log_service_with_generic_bank_holiday")
@patch.object(Logger, "warning")
def test_validate_opening_times_failure(
    mock_warning_logger: MagicMock,
    mock_log_service_with_generic_bank_holiday: MagicMock,
):
    # Arrange
    nhs_entity = MagicMock()
    nhs_entity.odscode.return_value = "12345"
    nhs_entity.all_times_valid.return_value = False
    dos_service = MagicMock()
    dos_service.any_generic_bankholiday_open_periods.return_value = True
    # Act
    result = validate_opening_times(dos_service, nhs_entity)
    # Assert
    assert result is False
    mock_warning_logger.assert_called_once_with(
        f"Opening Times for NHS Entity '{nhs_entity.odscode}' were previously found "
        "to be invalid or illogical. Skipping change.",
    )
    mock_log_service_with_generic_bank_holiday.assert_called_once_with(nhs_entity, dos_service)


@pytest.mark.parametrize(
    "website",
    [
        "www.test.com",
        "www.test.com/TEST",
        "www.rowlandspharmacy.co.uk/test?foo=test",
        "https://www.rowlandspharmacy.co.uk/test?foo=test",
    ],
)
@patch(f"{FILE_PATH}.log_website_is_invalid")
def test_validate_website_sucess(mock_log_website_is_invalid: MagicMock, website: str):
    # Act & Assert
    assert True is validate_website(nhs_entity=NHSEntity({}), nhs_website=website, dos_service=MagicMock())
    mock_log_website_is_invalid.assert_not_called()


@pytest.mark.parametrize(
    "website",
    [
        "https://testpharmacy@gmail.com",
        "test@test.com",
    ],
)
@patch(f"{FILE_PATH}.log_website_is_invalid")
def test_validate_website_failure(mock_log_website_is_invalid: MagicMock, website: str):
    # Arrange
    nhs_entity = NHSEntity({})
    dos_service = MagicMock()
    # Act & Assert
    assert False is validate_website(nhs_entity=nhs_entity, nhs_website=website, dos_service=dos_service)
    mock_log_website_is_invalid.assert_called_once_with(nhs_entity, website, dos_service)
