from datetime import date, time
from unittest.mock import MagicMock, call, patch

from application.common.constants import (
    DOS_BLOOD_PRESSURE_SYMPTOM_DISCRIMINATOR,
    DOS_BLOOD_PRESSURE_SYMPTOM_GROUP,
    DOS_CONTRACEPTION_SYMPTOM_DISCRIMINATOR,
    DOS_CONTRACEPTION_SYMPTOM_GROUP,
    DOS_PALLIATIVE_CARE_SYMPTOM_DISCRIMINATOR,
    DOS_PALLIATIVE_CARE_SYMPTOM_GROUP,
)
from application.common.opening_times import OpenPeriod, SpecifiedOpeningTime
from application.service_sync.data_processing.update_dos import (
    save_blood_pressure_into_db,
    save_contraception_into_db,
    save_demographics_into_db,
    save_palliative_care_into_db,
    save_specified_opening_times_into_db,
    save_standard_opening_times_into_db,
    update_dos_data,
)

FILE_PATH = "application.service_sync.data_processing.update_dos"


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
        dos_service=changes_to_dos.dos_service,
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
        dos_service=changes_to_dos.dos_service,
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


@patch(f"{FILE_PATH}.validate_z_code_exists")
@patch(f"{FILE_PATH}.query_dos_db")
def test_save_palliative_care_into_db_insert(
    mock_query_dos_db: MagicMock,
    mock_validate_z_code_exists: MagicMock,
):
    # Arrange
    mock_connection = MagicMock()
    dos_service = MagicMock()
    palliative_care = True
    mock_validate_z_code_exists.return_value = True
    # Act
    response = save_palliative_care_into_db(mock_connection, dos_service, True, palliative_care)
    # Assert
    assert True is response
    mock_validate_z_code_exists.assert_called_once_with(
        connection=mock_connection,
        dos_service=dos_service,
        symptom_group_id=DOS_PALLIATIVE_CARE_SYMPTOM_GROUP,
        symptom_discriminator_id=DOS_PALLIATIVE_CARE_SYMPTOM_DISCRIMINATOR,
        z_code_alias="Palliative Care",
    )
    mock_query_dos_db.assert_called_once_with(
        connection=mock_connection,
        query="INSERT INTO servicesgsds (serviceid, sdid, sgid) VALUES (%(SERVICE_ID)s, %(SDID)s, %(SGID)s);",
        query_vars={"SERVICE_ID": dos_service.id, "SDID": 14167, "SGID": 360},
    )


@patch(f"{FILE_PATH}.validate_z_code_exists")
@patch(f"{FILE_PATH}.query_dos_db")
def test_save_palliative_care_into_db_delete(
    mock_query_dos_db: MagicMock,
    mock_validate_z_code_exists: MagicMock,
):
    # Arrange
    mock_connection = MagicMock()
    dos_service = MagicMock()
    palliative_care = False
    mock_validate_z_code_exists.return_value = True
    # Act
    response = save_palliative_care_into_db(mock_connection, dos_service, True, palliative_care)
    # Assert
    assert True is response
    mock_validate_z_code_exists.assert_called_once_with(
        connection=mock_connection,
        dos_service=dos_service,
        symptom_group_id=DOS_PALLIATIVE_CARE_SYMPTOM_GROUP,
        symptom_discriminator_id=DOS_PALLIATIVE_CARE_SYMPTOM_DISCRIMINATOR,
        z_code_alias="Palliative Care",
    )
    mock_query_dos_db.assert_called_once_with(
        connection=mock_connection,
        query="DELETE FROM servicesgsds WHERE serviceid=%(SERVICE_ID)s AND sdid=%(SDID)s AND sgid=%(SGID)s;",
        query_vars={"SERVICE_ID": dos_service.id, "SDID": 14167, "SGID": 360},
    )


@patch(f"{FILE_PATH}.add_metric")
@patch(f"{FILE_PATH}.validate_z_code_exists")
@patch(f"{FILE_PATH}.query_dos_db")
def test_save_palliative_care_into_db_no_z_code(
    mock_query_dos_db: MagicMock,
    mock_validate_z_code_exists: MagicMock,
    mock_add_metric: MagicMock,
):
    # Arrange
    mock_connection = MagicMock()
    dos_service = MagicMock()
    palliative_care = True
    mock_validate_z_code_exists.return_value = False
    # Act
    response = save_palliative_care_into_db(mock_connection, dos_service, True, palliative_care)
    # Assert
    assert False is response
    mock_validate_z_code_exists.assert_called_once_with(
        connection=mock_connection,
        dos_service=dos_service,
        symptom_group_id=DOS_PALLIATIVE_CARE_SYMPTOM_GROUP,
        symptom_discriminator_id=DOS_PALLIATIVE_CARE_SYMPTOM_DISCRIMINATOR,
        z_code_alias="Palliative Care",
    )
    mock_add_metric.assert_called_once_with("DoSPalliativeCareZCodeDoesNotExist")
    mock_query_dos_db.assert_not_called()


@patch(f"{FILE_PATH}.add_metric")
@patch(f"{FILE_PATH}.validate_z_code_exists")
@patch(f"{FILE_PATH}.query_dos_db")
def test_save_palliative_care_into_db_no_changes(
    mock_query_dos_db: MagicMock,
    mock_validate_z_code_exists: MagicMock,
    mock_add_metric: MagicMock,
):
    # Arrange
    mock_connection = MagicMock()
    dos_service = MagicMock()
    palliative_care = True
    # Act
    response = save_palliative_care_into_db(mock_connection, dos_service, False, palliative_care)
    # Assert
    assert False is response
    mock_validate_z_code_exists.assert_not_called()
    mock_add_metric.assert_not_called()
    mock_query_dos_db.assert_not_called()


@patch(f"{FILE_PATH}.validate_z_code_exists_on_service")
@patch(f"{FILE_PATH}.query_dos_db")
def test_save_blood_pressure_into_db_insert(
    mock_query_dos_db: MagicMock,
    mock_validate_z_code_exists_on_service: MagicMock,
):
    # Arrange
    mock_connection = MagicMock()
    dos_service = MagicMock()
    dos_service.typeid = 148
    blood_pressure = True
    service_histories = MagicMock()
    mock_validate_z_code_exists_on_service.return_value = True
    # Act
    response = save_blood_pressure_into_db(mock_connection, dos_service, True, blood_pressure, service_histories)
    # Assert
    assert response == (True, service_histories)
    mock_query_dos_db.assert_has_calls(
        calls=[
            call(
                connection=mock_connection,
                query="UPDATE services SET statusid=%(STATUS_ID)s WHERE id=%(SERVICE_ID)s;",
                query_vars={"STATUS_ID": 1, "SERVICE_ID": dos_service.id},
            ),
            call().close(),
        ],
    )


@patch(f"{FILE_PATH}.query_dos_db")
def test_save_blood_pressure_into_db_delete(mock_query_dos_db: MagicMock):
    # Arrange
    mock_connection = MagicMock()
    dos_service = MagicMock()
    dos_service.typeid = 148
    blood_pressure = False
    service_histories = MagicMock()
    # Act
    response = save_blood_pressure_into_db(mock_connection, dos_service, True, blood_pressure, service_histories)
    # Assert
    assert response == (True, service_histories)
    mock_query_dos_db.assert_has_calls(
        calls=[
            call(
                connection=mock_connection,
                query="UPDATE services SET statusid=%(STATUS_ID)s WHERE id=%(SERVICE_ID)s;",
                query_vars={"STATUS_ID": 2, "SERVICE_ID": dos_service.id},
            ),
            call().close(),
        ],
    )


@patch(f"{FILE_PATH}.query_dos_db")
def test_save_blood_pressure_into_db_no_changes(mock_query_dos_db: MagicMock):
    # Arrange
    mock_connection = MagicMock()
    dos_service = MagicMock()
    dos_service.typeid = 148
    blood_pressure = False
    service_histories = MagicMock()
    # Act
    response = save_blood_pressure_into_db(mock_connection, dos_service, False, blood_pressure, service_histories)
    # Assert
    assert response == (False, service_histories)
    mock_query_dos_db.assert_not_called()


@patch(f"{FILE_PATH}.save_sgsdid_update")
@patch(f"{FILE_PATH}.validate_z_code_exists")
@patch(f"{FILE_PATH}.validate_z_code_exists_on_service")
@patch(f"{FILE_PATH}.query_dos_db")
def test_save_blood_pressure_into_db_z_code_not_exist(
    mock_query_dos_db: MagicMock,
    mock_validate_z_code_exists_on_service: MagicMock,
    mock_validate_z_code_exists: MagicMock,
    mock_save_sgsdid_update: MagicMock,
):
    # Arrange
    mock_connection = MagicMock()
    dos_service = MagicMock()
    dos_service.typeid = 148
    blood_pressure = True
    service_histories = MagicMock()
    mock_validate_z_code_exists_on_service.return_value = False
    mock_validate_z_code_exists.return_value = True
    # Act
    response = save_blood_pressure_into_db(mock_connection, dos_service, True, blood_pressure, service_histories)
    # Assert
    assert response == (True, service_histories)
    mock_query_dos_db.assert_has_calls(
        calls=[
            call(
                connection=mock_connection,
                query="UPDATE services SET statusid=%(STATUS_ID)s WHERE id=%(SERVICE_ID)s;",
                query_vars={"STATUS_ID": 1, "SERVICE_ID": dos_service.id},
            ),
            call().close(),
        ],
    )
    mock_save_sgsdid_update.assert_called_once_with(
        name="blood pressure",
        value=blood_pressure,
        sdid=DOS_BLOOD_PRESSURE_SYMPTOM_DISCRIMINATOR,
        sgid=DOS_BLOOD_PRESSURE_SYMPTOM_GROUP,
        dos_service=dos_service,
        connection=mock_connection,
    )


@patch(f"{FILE_PATH}.add_metric")
@patch(f"{FILE_PATH}.save_sgsdid_update")
@patch(f"{FILE_PATH}.validate_z_code_exists")
@patch(f"{FILE_PATH}.validate_z_code_exists_on_service")
@patch(f"{FILE_PATH}.query_dos_db")
def test_save_blood_pressure_into_db_z_not_valid(
    mock_query_dos_db: MagicMock,
    mock_validate_z_code_exists_on_service: MagicMock,
    mock_validate_z_code_exists: MagicMock,
    mock_save_sgsdid_update: MagicMock,
    mock_add_metric: MagicMock,
):
    # Arrange
    mock_connection = MagicMock()
    dos_service = MagicMock()
    dos_service.typeid = 148
    blood_pressure = True
    service_histories = MagicMock()
    mock_validate_z_code_exists_on_service.return_value = False
    mock_validate_z_code_exists.return_value = False
    # Act
    response = save_blood_pressure_into_db(mock_connection, dos_service, True, blood_pressure, service_histories)
    # Assert
    assert response == (False, service_histories)
    mock_query_dos_db.assert_has_calls(
        calls=[
            call(
                connection=mock_connection,
                query="UPDATE services SET statusid=%(STATUS_ID)s WHERE id=%(SERVICE_ID)s;",
                query_vars={"STATUS_ID": 1, "SERVICE_ID": dos_service.id},
            ),
            call().close(),
        ],
    )
    mock_save_sgsdid_update.assert_not_called()
    mock_add_metric.assert_called_once_with("DoSBloodPressureZCodeDoesNotExist")


@patch(f"{FILE_PATH}.validate_z_code_exists_on_service")
@patch(f"{FILE_PATH}.query_dos_db")
def test_save_contraception_into_db_insert(
    mock_query_dos_db: MagicMock,
    mock_validate_z_code_exists_on_service: MagicMock,
):
    # Arrange
    mock_connection = MagicMock()
    dos_service = MagicMock()
    dos_service.typeid = 149
    contraception = True
    service_histories = MagicMock()
    mock_validate_z_code_exists_on_service.return_value = True
    # Act
    response = save_contraception_into_db(mock_connection, dos_service, True, contraception, service_histories)
    # Assert
    assert response == (True, service_histories)
    mock_query_dos_db.assert_has_calls(
        calls=[
            call(
                connection=mock_connection,
                query="UPDATE services SET statusid=%(STATUS_ID)s WHERE id=%(SERVICE_ID)s;",
                query_vars={"STATUS_ID": 1, "SERVICE_ID": dos_service.id},
            ),
            call().close(),
        ],
    )


@patch(f"{FILE_PATH}.query_dos_db")
def test_save_contraception_into_db_delete(mock_query_dos_db: MagicMock):
    # Arrange
    mock_connection = MagicMock()
    dos_service = MagicMock()
    dos_service.typeid = 149
    contraception = False
    service_histories = MagicMock()
    # Act
    response = save_contraception_into_db(mock_connection, dos_service, True, contraception, service_histories)
    # Assert
    assert response == (True, service_histories)
    mock_query_dos_db.assert_has_calls(
        calls=[
            call(
                connection=mock_connection,
                query="UPDATE services SET statusid=%(STATUS_ID)s WHERE id=%(SERVICE_ID)s;",
                query_vars={"STATUS_ID": 2, "SERVICE_ID": dos_service.id},
            ),
            call().close(),
        ],
    )


@patch(f"{FILE_PATH}.query_dos_db")
def test_save_contraception_into_db_no_changes(mock_query_dos_db: MagicMock):
    # Arrange
    mock_connection = MagicMock()
    dos_service = MagicMock()
    dos_service.typeid = 149
    contraception = False
    service_histories = MagicMock()
    # Act
    response = save_contraception_into_db(mock_connection, dos_service, False, contraception, service_histories)
    # Assert
    assert response == (False, service_histories)
    mock_query_dos_db.assert_not_called()


@patch(f"{FILE_PATH}.save_sgsdid_update")
@patch(f"{FILE_PATH}.validate_z_code_exists")
@patch(f"{FILE_PATH}.validate_z_code_exists_on_service")
@patch(f"{FILE_PATH}.query_dos_db")
def test_save_contraception_into_db_z_code_not_exist(
    mock_query_dos_db: MagicMock,
    mock_validate_z_code_exists_on_service: MagicMock,
    mock_validate_z_code_exists: MagicMock,
    mock_save_sgsdid_update: MagicMock,
):
    # Arrange
    mock_connection = MagicMock()
    dos_service = MagicMock()
    dos_service.typeid = 149
    contraception = True
    service_histories = MagicMock()
    mock_validate_z_code_exists_on_service.return_value = False
    mock_validate_z_code_exists.return_value = True
    # Act
    response = save_contraception_into_db(mock_connection, dos_service, True, contraception, service_histories)
    # Assert
    assert response == (True, service_histories)
    mock_query_dos_db.assert_has_calls(
        calls=[
            call(
                connection=mock_connection,
                query="UPDATE services SET statusid=%(STATUS_ID)s WHERE id=%(SERVICE_ID)s;",
                query_vars={"STATUS_ID": 1, "SERVICE_ID": dos_service.id},
            ),
            call().close(),
        ],
    )
    mock_save_sgsdid_update.assert_called_once_with(
        name="contraception",
        value=contraception,
        sdid=DOS_CONTRACEPTION_SYMPTOM_DISCRIMINATOR,
        sgid=DOS_CONTRACEPTION_SYMPTOM_GROUP,
        dos_service=dos_service,
        connection=mock_connection,
    )


@patch(f"{FILE_PATH}.add_metric")
@patch(f"{FILE_PATH}.save_sgsdid_update")
@patch(f"{FILE_PATH}.validate_z_code_exists")
@patch(f"{FILE_PATH}.validate_z_code_exists_on_service")
@patch(f"{FILE_PATH}.query_dos_db")
def test_save_contraception_into_db_z_not_valid(
    mock_query_dos_db: MagicMock,
    mock_validate_z_code_exists_on_service: MagicMock,
    mock_validate_z_code_exists: MagicMock,
    mock_save_sgsdid_update: MagicMock,
    mock_add_metric: MagicMock,
):
    # Arrange
    mock_connection = MagicMock()
    dos_service = MagicMock()
    dos_service.typeid = 149
    contraception = True
    service_histories = MagicMock()
    mock_validate_z_code_exists_on_service.return_value = False
    mock_validate_z_code_exists.return_value = False
    # Act
    response = save_contraception_into_db(mock_connection, dos_service, True, contraception, service_histories)
    # Assert
    assert response == (False, service_histories)
    mock_query_dos_db.assert_has_calls(
        calls=[
            call(
                connection=mock_connection,
                query="UPDATE services SET statusid=%(STATUS_ID)s WHERE id=%(SERVICE_ID)s;",
                query_vars={"STATUS_ID": 1, "SERVICE_ID": dos_service.id},
            ),
            call().close(),
        ],
    )
    mock_save_sgsdid_update.assert_not_called()
    mock_add_metric.assert_called_once_with("DoSContraceptionZCodeDoesNotExist")
