from unittest.mock import MagicMock, call, patch

from application.common.constants import DOS_PALLIATIVE_CARE_SYMPTOM_DISCRIMINATOR, DOS_PALLIATIVE_CARE_SYMPTOM_GROUP
from application.service_sync.validate_dos_data import validate_dos_z_code_exists

FILE_PATH = "application.service_sync.validate_dos_data"


@patch(f"{FILE_PATH}.query_dos_db")
def test_validate_dos_z_code_exists(mock_query_dos_db: MagicMock) -> None:
    # Arrange
    mock_connection = MagicMock()
    mock_query_dos_db.return_value.rowcount = 1
    dos_service = MagicMock()
    # Act
    response = validate_dos_z_code_exists(
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
def test_validate_dos_z_code_existss_does_not_exist(mock_query_dos_db: MagicMock) -> None:
    # Arrange
    mock_connection = MagicMock()
    mock_query_dos_db.return_value.rowcount = 0
    dos_service = MagicMock()
    # Act
    response = validate_dos_z_code_exists(
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
