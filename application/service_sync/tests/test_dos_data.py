from datetime import date, time
from unittest.mock import MagicMock, call, patch

import pytest

from application.common.opening_times import OpenPeriod, SpecifiedOpeningTime
from application.service_sync.dos_data import (
    get_dos_service_and_history,
    save_demographics_into_db,
    save_palliative_care_into_db,
    save_specified_opening_times_into_db,
    save_standard_opening_times_into_db,
    update_dos_data,
    validate_dos_palliative_care_z_code_exists,
)

FILE_PATH = "application.service_sync.dos_data"


@patch(f"{FILE_PATH}.ServiceHistories")
@patch(f"{FILE_PATH}.get_specified_opening_times_from_db")
@patch(f"{FILE_PATH}.get_standard_opening_times_from_db")
@patch(f"{FILE_PATH}.DoSService")
@patch(f"{FILE_PATH}.query_dos_db")
@patch(f"{FILE_PATH}.connect_to_dos_db")
def test_get_dos_service_and_history(
    mock_connect_to_dos_db: MagicMock,
    mock_query_dos_db: MagicMock,
    mock_dos_service: MagicMock,
    mock_get_standard_opening_times_from_db: MagicMock,
    mock_get_specified_opening_times_from_db: MagicMock,
    mock_service_histories: MagicMock,
):
    # Arrange
    service_id = 12345
    mock_query_dos_db.return_value.fetchall.return_value = [["Test"]]
    # Act
    dos_service, service_history = get_dos_service_and_history(service_id)
    # Assert
    assert mock_dos_service() == dos_service
    mock_get_standard_opening_times_from_db.assert_called_once_with(
        connection=mock_connect_to_dos_db().__enter__(),
        service_id=service_id,
    )
    mock_get_specified_opening_times_from_db.assert_called_once_with(
        connection=mock_connect_to_dos_db().__enter__(),
        service_id=service_id,
    )
    assert mock_service_histories() == service_history
    mock_service_histories.return_value.get_service_history_from_db.assert_called_once_with(
        mock_connect_to_dos_db().__enter__(),
    )
    mock_service_histories.return_value.create_service_histories_entry.assert_called_once_with()


@patch(f"{FILE_PATH}.query_dos_db")
@patch(f"{FILE_PATH}.connect_to_dos_db")
def test_get_dos_service_and_history_no_match(
    mock_connect_to_dos_db: MagicMock,
    mock_query_dos_db: MagicMock,
):
    # Arrange
    service_id = 12345
    mock_query_dos_db.return_value.fetchall.return_value = []
    # Act
    with pytest.raises(ValueError, match=f"Service ID {service_id} not found"):
        get_dos_service_and_history(service_id)
    mock_connect_to_dos_db.assert_called_once()


@patch(f"{FILE_PATH}.query_dos_db")
@patch(f"{FILE_PATH}.connect_to_dos_db")
def test_get_dos_service_and_history_mutiple_matches(
    mock_connect_to_dos_db: MagicMock,
    mock_query_dos_db: MagicMock,
):
    # Arrange
    service_id = 12345
    mock_query_dos_db.return_value.fetchall.return_value = [["Test"], ["Test"]]
    # Act
    with pytest.raises(ValueError, match=f"Multiple services found for Service Id: {service_id}"):
        get_dos_service_and_history(service_id)
    mock_connect_to_dos_db.assert_called_once()


@patch(f"{FILE_PATH}.log_service_updates")
@patch(f"{FILE_PATH}.save_palliative_care_into_db")
@patch(f"{FILE_PATH}.save_specified_opening_times_into_db")
@patch(f"{FILE_PATH}.save_standard_opening_times_into_db")
@patch(f"{FILE_PATH}.save_demographics_into_db")
@patch(f"{FILE_PATH}.connect_to_dos_db")
def test_update_dos_data(
    mock_connect_to_dos_db: MagicMock,
    mock_save_demographics_into_db: MagicMock,
    mock_save_standard_opening_times_into_db: MagicMock,
    mock_save_specified_opening_times_into_db: MagicMock,
    mock_save_palliative_care_into_db: MagicMock,
    mock_log_service_updates: MagicMock,
):
    # Arrange
    changes_to_dos = MagicMock()
    service_histories = MagicMock()
    service_id = 1
    # Act
    update_dos_data(changes_to_dos, service_id, service_histories)
    # Assert
    mock_save_demographics_into_db.assert_called_once_with(
        connection=mock_connect_to_dos_db().__enter__(),
        service_id=service_id,
        demographics_changes=changes_to_dos.demographic_changes,
    )
    mock_save_standard_opening_times_into_db.assert_called_once_with(
        connection=mock_connect_to_dos_db().__enter__(),
        service_id=service_id,
        standard_opening_times_changes=changes_to_dos.standard_opening_times_changes,
    )
    mock_save_specified_opening_times_into_db.assert_called_once_with(
        connection=mock_connect_to_dos_db().__enter__(),
        service_id=service_id,
        is_changes=changes_to_dos.specified_opening_times_changes,
        specified_opening_times_changes=changes_to_dos.new_specified_opening_times,
    )
    mock_save_palliative_care_into_db.assert_called_once_with(
        connection=mock_connect_to_dos_db().__enter__(),
        service_id=service_id,
        is_changes=changes_to_dos.palliative_care_changes,
        palliative_care=changes_to_dos.nhs_entity.palliative_care,
    )
    service_histories.save_service_histories.assert_called_once_with(connection=mock_connect_to_dos_db().__enter__())
    mock_connect_to_dos_db.return_value.__enter__.return_value.commit.assert_called_once()
    mock_connect_to_dos_db.return_value.__enter__.return_value.close.assert_called_once()
    mock_log_service_updates.assert_called_once_with(changes_to_dos=changes_to_dos, service_histories=service_histories)


@patch(f"{FILE_PATH}.save_palliative_care_into_db")
@patch(f"{FILE_PATH}.save_specified_opening_times_into_db")
@patch(f"{FILE_PATH}.save_standard_opening_times_into_db")
@patch(f"{FILE_PATH}.save_demographics_into_db")
@patch(f"{FILE_PATH}.connect_to_dos_db")
def test_update_dos_data_no_changes(
    mock_connect_to_dos_db: MagicMock,
    mock_save_demographics_into_db: MagicMock,
    mock_save_standard_opening_times_into_db: MagicMock,
    mock_save_specified_opening_times_into_db: MagicMock,
    mock_save_palliative_care_into_db: MagicMock,
):
    # Arrange
    changes_to_dos = MagicMock()
    service_histories = MagicMock()
    service_id = 1
    mock_save_demographics_into_db.return_value = False
    mock_save_standard_opening_times_into_db.return_value = False
    mock_save_specified_opening_times_into_db.return_value = False
    mock_save_palliative_care_into_db.return_value = False
    # Act
    update_dos_data(changes_to_dos, service_id, service_histories)
    # Assert
    mock_save_demographics_into_db.assert_called_once_with(
        connection=mock_connect_to_dos_db().__enter__(),
        service_id=service_id,
        demographics_changes=changes_to_dos.demographic_changes,
    )
    mock_save_standard_opening_times_into_db.assert_called_once_with(
        connection=mock_connect_to_dos_db().__enter__(),
        service_id=service_id,
        standard_opening_times_changes=changes_to_dos.standard_opening_times_changes,
    )
    mock_save_specified_opening_times_into_db.assert_called_once_with(
        connection=mock_connect_to_dos_db().__enter__(),
        service_id=service_id,
        is_changes=changes_to_dos.specified_opening_times_changes,
        specified_opening_times_changes=changes_to_dos.new_specified_opening_times,
    )
    mock_save_palliative_care_into_db.assert_called_once_with(
        connection=mock_connect_to_dos_db().__enter__(),
        service_id=service_id,
        is_changes=changes_to_dos.palliative_care_changes,
        palliative_care=changes_to_dos.nhs_entity.palliative_care,
    )
    service_histories.save_service_histories.assert_not_called()
    mock_connect_to_dos_db.return_value.__enter__.return_value.close.assert_called_once()


@patch(f"{FILE_PATH}.SQL")
@patch(f"{FILE_PATH}.query_dos_db")
def test_save_demographics_into_db(mock_query_dos_db: MagicMock, mock_sql: MagicMock):
    # Arrange
    mock_connection = MagicMock()
    service_id = 1
    demographics_changes = {"test": "test"}
    mock_sql.return_value.format.return_value.as_string.return_value = query = "SELECT * FROM test"
    # Act
    response = save_demographics_into_db(mock_connection, service_id, demographics_changes)
    # Assert
    assert True is response
    mock_query_dos_db.assert_called_once_with(
        connection=mock_connection,
        query=query,
        query_vars={"SERVICE_ID": service_id},
    )


def test_save_demographics_into_db_no_changes():
    # Arrange
    mock_connection = MagicMock()
    service_id = 1
    demographics_changes = None
    # Act
    response = save_demographics_into_db(mock_connection, service_id, demographics_changes)
    # Assert
    assert False is response


@patch(f"{FILE_PATH}.query_dos_db")
def test_save_standard_opening_times_into_db(mock_query_dos_db: MagicMock):
    # Arrange
    mock_connection = MagicMock()
    service_id = 1
    open_period = OpenPeriod(time(1, 0, 0), time(2, 0, 0))
    standard_opening_times_changes = {
        1: [open_period],
        2: [open_period],
        3: [open_period],
        4: [open_period],
        5: [open_period],
        6: [open_period],
        7: [open_period],
    }
    # Act
    response = save_standard_opening_times_into_db(mock_connection, service_id, standard_opening_times_changes)
    # Assert
    assert True is response


@patch(f"{FILE_PATH}.query_dos_db")
def test_save_specified_opening_times_into_db(mock_query_dos_db: MagicMock):
    # Arrange
    mock_connection = MagicMock()
    service_id = 1
    open_period_list = [OpenPeriod(time(1, 0, 0), time(2, 0, 0))]
    specified_opening_time_list = [SpecifiedOpeningTime(open_period_list, date(2022, 12, 24), True)]
    # Act
    response = save_specified_opening_times_into_db(mock_connection, service_id, True, specified_opening_time_list)
    # Assert
    assert True is response


@patch(f"{FILE_PATH}.query_dos_db")
def test_save_specified_opening_times_into_db_closed(mock_query_dos_db: MagicMock):
    # Arrange
    mock_connection = MagicMock()
    service_id = 1
    open_period_list = [OpenPeriod(time(1, 0, 0), time(2, 0, 0))]
    specified_opening_time_list = [SpecifiedOpeningTime(open_period_list, date(2022, 12, 24), False)]
    # Act
    response = save_specified_opening_times_into_db(mock_connection, service_id, True, specified_opening_time_list)
    # Assert
    assert True is response


@patch(f"{FILE_PATH}.validate_dos_palliative_care_z_code_exists")
@patch(f"{FILE_PATH}.query_dos_db")
def test_save_palliative_care_into_db_insert(
    mock_query_dos_db: MagicMock,
    mock_validate_dos_palliative_care_z_code_exists: MagicMock,
):
    # Arrange
    mock_connection = MagicMock()
    service_id = 1
    palliative_care = True
    mock_validate_dos_palliative_care_z_code_exists.return_value = True
    # Act
    response = save_palliative_care_into_db(mock_connection, service_id, True, palliative_care)
    # Assert
    assert True is response
    mock_query_dos_db.assert_called_once_with(
        connection=mock_connection,
        query="INSERT INTO servicesgsds (serviceid, sdid, sgid) VALUES (%(SERVICE_ID)s, %(SDID)s, %(SGID)s);",
        query_vars={"SERVICE_ID": service_id, "SDID": 14167, "SGID": 360},
    )


@patch(f"{FILE_PATH}.validate_dos_palliative_care_z_code_exists")
@patch(f"{FILE_PATH}.query_dos_db")
def test_save_palliative_care_into_db_delete(
    mock_query_dos_db: MagicMock,
    mock_validate_dos_palliative_care_z_code_exists: MagicMock,
):
    # Arrange
    mock_connection = MagicMock()
    service_id = 1
    palliative_care = False
    mock_validate_dos_palliative_care_z_code_exists.return_value = True
    # Act
    response = save_palliative_care_into_db(mock_connection, service_id, True, palliative_care)
    # Assert
    assert True is response
    mock_query_dos_db.assert_called_once_with(
        connection=mock_connection,
        query="DELETE FROM servicesgsds WHERE serviceid=%(SERVICE_ID)s AND sdid=%(SDID)s AND sgid=%(SGID)s;",
        query_vars={"SERVICE_ID": service_id, "SDID": 14167, "SGID": 360},
    )


@patch(f"{FILE_PATH}.add_metric")
@patch(f"{FILE_PATH}.validate_dos_palliative_care_z_code_exists")
@patch(f"{FILE_PATH}.query_dos_db")
def test_save_palliative_care_into_db_no_z_code(
    mock_query_dos_db: MagicMock,
    mock_validate_dos_palliative_care_z_code_exists: MagicMock,
    mock_add_metric: MagicMock,
):
    # Arrange
    mock_connection = MagicMock()
    service_id = 1
    palliative_care = True
    mock_validate_dos_palliative_care_z_code_exists.return_value = False
    # Act
    response = save_palliative_care_into_db(mock_connection, service_id, True, palliative_care)
    # Assert
    assert False is response
    mock_add_metric.assert_called_once_with("DoSPalliativeCareZCodeDoesNotExist")
    mock_query_dos_db.assert_not_called()


@patch(f"{FILE_PATH}.add_metric")
@patch(f"{FILE_PATH}.validate_dos_palliative_care_z_code_exists")
@patch(f"{FILE_PATH}.query_dos_db")
def test_save_palliative_care_into_db_no_change(
    mock_query_dos_db: MagicMock,
    mock_validate_dos_palliative_care_z_code_exists: MagicMock,
    mock_add_metric: MagicMock,
):
    # Arrange
    mock_connection = MagicMock()
    service_id = 1
    palliative_care = True
    mock_validate_dos_palliative_care_z_code_exists.return_value = True
    # Act
    response = save_palliative_care_into_db(mock_connection, service_id, False, palliative_care)
    # Assert
    assert False is response
    mock_add_metric.assert_not_called()
    mock_query_dos_db.assert_not_called()


@patch(f"{FILE_PATH}.query_dos_db")
def test_validate_dos_palliative_care_z_code_exists(mock_query_dos_db: MagicMock):
    # Arrange
    mock_connection = MagicMock()
    mock_query_dos_db.return_value.rowcount = 1
    # Act
    response = validate_dos_palliative_care_z_code_exists(mock_connection)
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
def test_validate_dos_palliative_care_z_code_exists_does_not_exist(mock_query_dos_db: MagicMock):
    # Arrange
    mock_connection = MagicMock()
    mock_query_dos_db.return_value.rowcount = 0
    # Act
    response = validate_dos_palliative_care_z_code_exists(mock_connection)
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
