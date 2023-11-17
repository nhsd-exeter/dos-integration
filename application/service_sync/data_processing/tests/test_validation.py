from unittest.mock import MagicMock, call, patch

import pytest
from aws_lambda_powertools.logging import Logger

from application.common.constants import DOS_PALLIATIVE_CARE_SYMPTOM_DISCRIMINATOR, DOS_PALLIATIVE_CARE_SYMPTOM_GROUP
from application.common.nhs import NHSEntity
from application.service_sync.data_processing.validation import (
    validate_opening_times,
    validate_website,
    validate_z_code_exists,
)

FILE_PATH = "application.service_sync.data_processing.validation"


@patch(f"{FILE_PATH}.log_service_with_generic_bank_holiday")
@patch.object(Logger, "warning")
def test_validate_opening_times_sucessful(
    mock_warning_logger: MagicMock,
    mock_log_service_with_generic_bank_holiday: MagicMock,
) -> None:
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
) -> None:
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
def test_validate_website_sucess(mock_log_website_is_invalid: MagicMock, website: str) -> None:
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
def test_validate_website_failure(mock_log_website_is_invalid: MagicMock, website: str) -> None:
    # Arrange
    nhs_entity = NHSEntity({})
    dos_service = MagicMock()
    # Act & Assert
    assert False is validate_website(nhs_entity=nhs_entity, nhs_website=website, dos_service=dos_service)
    mock_log_website_is_invalid.assert_called_once_with(nhs_entity, website, dos_service)


@patch(f"{FILE_PATH}.query_dos_db")
def test_validate_z_code_exists(mock_query_dos_db: MagicMock) -> None:
    # Arrange
    mock_connection = MagicMock()
    mock_query_dos_db.return_value.rowcount = 1
    dos_service = MagicMock()
    # Act
    response = validate_z_code_exists(
        connection=mock_connection,
        dos_service=dos_service,
        symptom_group_id=DOS_PALLIATIVE_CARE_SYMPTOM_GROUP,
        symptom_discriminator_id=DOS_PALLIATIVE_CARE_SYMPTOM_DISCRIMINATOR,
        z_code_alias="Palliative Care",
    )
    # Assert
    assert True is response
    mock_query_dos_db.assert_has_calls(
        calls=[
            call(
                connection=mock_connection,
                query=(
                    "SELECT id FROM symptomgroupsymptomdiscriminators WHERE symptomgroupid=%(SGID)s "
                    "AND symptomdiscriminatorid=%(SDID)s;"
                ),
                query_vars={"SGID": 360, "SDID": 14167},
            ),
            call().close(),
        ],
    )


@patch(f"{FILE_PATH}.query_dos_db")
def test_validate_z_code_existss_does_not_exist(mock_query_dos_db: MagicMock) -> None:
    # Arrange
    mock_connection = MagicMock()
    mock_query_dos_db.return_value.rowcount = 0
    dos_service = MagicMock()
    # Act
    response = validate_z_code_exists(
        connection=mock_connection,
        dos_service=dos_service,
        symptom_group_id=DOS_PALLIATIVE_CARE_SYMPTOM_GROUP,
        symptom_discriminator_id=DOS_PALLIATIVE_CARE_SYMPTOM_DISCRIMINATOR,
        z_code_alias="Palliative Care",
    )
    # Assert
    assert False is response
    mock_query_dos_db.assert_has_calls(
        calls=[
            call(
                connection=mock_connection,
                query=(
                    "SELECT id FROM symptomgroupsymptomdiscriminators WHERE symptomgroupid=%(SGID)s "
                    "AND symptomdiscriminatorid=%(SDID)s;"
                ),
                query_vars={"SGID": 360, "SDID": 14167},
            ),
            call().close(),
        ],
    )
