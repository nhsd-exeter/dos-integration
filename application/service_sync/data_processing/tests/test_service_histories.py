from datetime import date, time
from json import dumps
from unittest.mock import MagicMock, patch

from psycopg.rows import dict_row

from application.common.constants import (
    DOS_SGSDID_CHANGE_KEY,
    DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_MONDAY_CHANGE_KEY,
)
from application.common.opening_times import OpenPeriod, SpecifiedOpeningTime
from application.service_sync.data_processing.service_histories import ServiceHistories
from application.service_sync.data_processing.service_histories_change import ServiceHistoriesChange

FILE_PATH = "application.service_sync.data_processing.service_histories"
SERVICE_ID = 1


@patch(f"{FILE_PATH}.time")
def test_service_histories(mock_time: MagicMock) -> None:
    # Arrange
    mock_time.return_value = time = 123
    # Act
    service_histories = ServiceHistories(service_id=SERVICE_ID)
    # Assert
    assert "new_change" == service_histories.NEW_CHANGE_KEY
    assert {} == service_histories.service_history
    assert {} == service_histories.existing_service_history
    assert service_histories.service_id == SERVICE_ID
    assert time == service_histories.current_epoch_time
    mock_time.assert_called_once()


def test_service_histories_get_service_history_from_db_rows_returned() -> None:
    # Arrange
    service_history = ServiceHistories(service_id=SERVICE_ID)
    mock_connection = MagicMock()
    change = {"new_change": 123}
    service_history_data = {"history": dumps(change)}
    mock_connection.cursor.return_value.fetchall.return_value = [service_history_data]
    # Act
    service_history.get_service_history_from_db(mock_connection)
    # Assert
    assert True is service_history.history_already_exists
    assert change == service_history.existing_service_history
    mock_connection.cursor.assert_called_once_with(row_factory=dict_row)
    mock_connection.cursor.return_value.execute.assert_called_once_with(
        query="Select history from servicehistories where serviceid = %(SERVICE_ID)s",
        params={"SERVICE_ID": SERVICE_ID},
    )
    mock_connection.cursor.return_value.fetchall.assert_called_once()


def test_service_histories_get_service_history_from_db_no_rows_returned() -> None:
    # Arrange
    service_history = ServiceHistories(service_id=SERVICE_ID)
    mock_connection = MagicMock()
    mock_connection.cursor.return_value.fetchall.return_value = []
    # Act
    service_history.get_service_history_from_db(mock_connection)
    # Assert
    assert False is service_history.history_already_exists
    assert {} == service_history.existing_service_history
    mock_connection.cursor.assert_called_once_with(row_factory=dict_row)
    mock_connection.cursor.return_value.execute.assert_called_once_with(
        query="Select history from servicehistories where serviceid = %(SERVICE_ID)s",
        params={"SERVICE_ID": SERVICE_ID},
    )

    mock_connection.cursor.return_value.fetchall.assert_called_once()


def test_service_histories_create_service_histories_entry_no_history_already_exists() -> None:
    # Arrange
    service_history = ServiceHistories(service_id=SERVICE_ID)
    # Act
    service_history.create_service_histories_entry()
    # Assert
    assert {
        service_history.NEW_CHANGE_KEY: {
            "new": {},
            "initiator": {"userid": "DOS_INTEGRATION", "timestamp": "TBD"},
            "approver": {"userid": "DOS_INTEGRATION", "timestamp": "TBD"},
        },
    } == service_history.service_history


def test_service_histories_add_change() -> None:
    # Arrange
    change_key = "change_key"
    service_history = ServiceHistories(service_id=SERVICE_ID)
    service_history.create_service_histories_entry()
    mock_service_history_change = MagicMock()
    mock_service_history_change.get_change.return_value = change = "change"
    # Act
    service_history.add_change(change_key, mock_service_history_change)
    # Assert
    assert {
        service_history.NEW_CHANGE_KEY: {
            "new": {change_key: change},
            "initiator": {"userid": "DOS_INTEGRATION", "timestamp": "TBD"},
            "approver": {"userid": "DOS_INTEGRATION", "timestamp": "TBD"},
        },
    } == service_history.service_history
    mock_service_history_change.get_change.assert_called_once_with()


@patch(f"{FILE_PATH}.ServiceHistoriesChange")
def test_service_histories_add_standard_opening_times_change(mock_service_histories_change: MagicMock) -> None:
    # Arrange
    service_history = ServiceHistories(service_id=SERVICE_ID)
    service_history.add_change = mock_add_change = MagicMock()
    current_opening_times = MagicMock()
    current_opening_times.export_opening_times_in_seconds_for_day.return_value = current_opening_times_in_seconds = [
        "456-789",
    ]
    current_opening_times.export_opening_times_for_day.return_value = (
        current_opening_times_for_day
    ) = "current_opening_times_for_day"
    new_opening_times = MagicMock()
    new_opening_times.export_opening_times_in_seconds_for_day.return_value = new_opening_times_in_seconds = ["123-456"]
    weekday = "Monday"
    mock_service_histories_change.return_value = mock_service_histories_change_variable = MagicMock()
    # Act
    service_history.add_standard_opening_times_change(
        current_opening_times,
        new_opening_times,
        weekday,
        DOS_STANDARD_OPENING_TIMES_MONDAY_CHANGE_KEY,
    )
    # Assert
    mock_add_change.assert_called_once_with(
        dos_change_key=DOS_STANDARD_OPENING_TIMES_MONDAY_CHANGE_KEY,
        change=mock_service_histories_change_variable,
    )
    current_opening_times.export_opening_times_in_seconds_for_day.assert_called_once_with(weekday)
    new_opening_times.export_opening_times_in_seconds_for_day.assert_called_once_with(weekday)
    current_opening_times.export_opening_times_for_day.assert_called_once_with(weekday)
    mock_service_histories_change.assert_called_once_with(
        change_key=DOS_STANDARD_OPENING_TIMES_MONDAY_CHANGE_KEY,
        previous_value=current_opening_times_for_day,
        data={"remove": current_opening_times_in_seconds, "add": new_opening_times_in_seconds},
    )


@patch(f"{FILE_PATH}.ServiceHistoriesChange")
def test_service_histories_add_standard_opening_times_change_no_change(
    mock_service_histories_change: MagicMock,
) -> None:
    # Arrange
    service_history = ServiceHistories(service_id=SERVICE_ID)
    service_history.add_change = mock_add_change = MagicMock()
    current_opening_times = MagicMock()
    current_opening_times.export_opening_times_in_seconds_for_day.return_value = []
    current_opening_times.export_opening_times_for_day.return_value = (
        current_opening_times_for_day
    ) = "current_opening_times_for_day"
    new_opening_times = MagicMock()
    new_opening_times.export_opening_times_in_seconds_for_day.return_value = []
    weekday = "Monday"
    mock_service_histories_change.return_value = mock_service_histories_change_variable = MagicMock()
    # Act
    service_history.add_standard_opening_times_change(
        current_opening_times,
        new_opening_times,
        weekday,
        DOS_STANDARD_OPENING_TIMES_MONDAY_CHANGE_KEY,
    )
    # Assert
    mock_add_change.assert_called_once_with(
        dos_change_key=DOS_STANDARD_OPENING_TIMES_MONDAY_CHANGE_KEY,
        change=mock_service_histories_change_variable,
    )
    current_opening_times.export_opening_times_in_seconds_for_day.assert_called_once_with(weekday)
    new_opening_times.export_opening_times_in_seconds_for_day.assert_called_once_with(weekday)
    current_opening_times.export_opening_times_for_day.assert_called_once_with(weekday)
    mock_service_histories_change.assert_called_once_with(
        change_key=DOS_STANDARD_OPENING_TIMES_MONDAY_CHANGE_KEY,
        previous_value=current_opening_times_for_day,
        data={},
    )


@patch(f"{FILE_PATH}.ServiceHistories.get_formatted_specified_opening_times")
@patch(f"{FILE_PATH}.ServiceHistoriesChange")
def test_service_histories_add_specified_opening_times_change_modify(
    mock_service_histories_change: MagicMock,
    mock_get_formatted_specified_opening_times: MagicMock,
) -> None:
    # Arrange
    service_history = ServiceHistories(service_id=SERVICE_ID)
    service_history.add_change = mock_add_change = MagicMock()
    current_opening_times = MagicMock()
    formatted_current_opening_times = [
        "2030-12-30-closed",
        "2030-12-31-1000-2000",
        "2030-12-31-3000-4000",
    ]
    new_opening_times = MagicMock()
    formatted_new_opening_times = [
        "2030-12-28-closed",
        "2030-12-29-1000-2000",
        "2030-12-29-3000-4000",
    ]
    mock_get_formatted_specified_opening_times.side_effect = [
        formatted_current_opening_times,
        formatted_new_opening_times,
    ]
    mock_service_histories_change.return_value = mock_service_histories_change_variable = MagicMock()
    # Act
    service_history.add_specified_opening_times_change(current_opening_times, new_opening_times)
    # Assert
    mock_add_change.assert_called_once_with(
        dos_change_key=DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY,
        change=mock_service_histories_change_variable,
    )
    mock_service_histories_change.assert_called_once_with(
        change_key=DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY,
        previous_value=formatted_current_opening_times,
        data={"remove": formatted_current_opening_times, "add": formatted_new_opening_times},
    )


@patch(f"{FILE_PATH}.ServiceHistories.get_formatted_specified_opening_times")
@patch(f"{FILE_PATH}.ServiceHistoriesChange")
def test_service_histories_add_specified_opening_times_change_add(
    mock_service_histories_change: MagicMock,
    mock_get_formatted_specified_opening_times: MagicMock,
) -> None:
    # Arrange
    service_history = ServiceHistories(service_id=SERVICE_ID)
    service_history.add_change = mock_add_change = MagicMock()
    current_opening_times = MagicMock()
    new_opening_times = MagicMock()
    formatted_new_opening_times = [
        "2030-12-28-closed",
        "2030-12-29-1000-2000",
        "2030-12-29-3000-4000",
    ]
    mock_get_formatted_specified_opening_times.side_effect = [
        [],
        formatted_new_opening_times,
    ]
    mock_service_histories_change.return_value = mock_service_histories_change_variable = MagicMock()
    # Act
    service_history.add_specified_opening_times_change(current_opening_times, new_opening_times)
    # Assert
    mock_add_change.assert_called_once_with(
        dos_change_key=DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY,
        change=mock_service_histories_change_variable,
    )
    mock_service_histories_change.assert_called_once_with(
        change_key=DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY,
        previous_value=[],
        data={"add": formatted_new_opening_times},
    )


@patch(f"{FILE_PATH}.ServiceHistories.get_formatted_specified_opening_times")
@patch(f"{FILE_PATH}.ServiceHistoriesChange")
def test_service_histories_add_specified_opening_times_change_remove(
    mock_service_histories_change: MagicMock,
    mock_get_formatted_specified_opening_times: MagicMock,
) -> None:
    # Arrange
    service_history = ServiceHistories(service_id=SERVICE_ID)
    service_history.add_change = mock_add_change = MagicMock()
    current_opening_times = MagicMock()
    formatted_current_opening_times = [
        "2030-12-30-closed",
        "2030-12-31-1000-2000",
        "2030-12-31-3000-4000",
    ]
    new_opening_times = MagicMock()
    mock_get_formatted_specified_opening_times.side_effect = [
        formatted_current_opening_times,
        [],
    ]
    mock_service_histories_change.return_value = mock_service_histories_change_variable = MagicMock()
    # Act
    service_history.add_specified_opening_times_change(current_opening_times, new_opening_times)
    # Assert
    mock_add_change.assert_called_once_with(
        dos_change_key=DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY,
        change=mock_service_histories_change_variable,
    )
    mock_service_histories_change.assert_called_once_with(
        change_key=DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY,
        previous_value=formatted_current_opening_times,
        data={
            "remove": formatted_current_opening_times,
        },
    )


@patch(f"{FILE_PATH}.ServiceHistories.get_formatted_specified_opening_times")
@patch(f"{FILE_PATH}.ServiceHistoriesChange")
def test_service_histories_add_specified_opening_times_change_no_change(
    mock_service_histories_change: MagicMock,
    mock_get_formatted_specified_opening_times: MagicMock,
) -> None:
    # Arrange
    service_history = ServiceHistories(service_id=SERVICE_ID)
    service_history.add_change = mock_add_change = MagicMock()
    current_opening_times = MagicMock()
    new_opening_times = MagicMock()
    mock_get_formatted_specified_opening_times.side_effect = [[], []]
    mock_service_histories_change.return_value = mock_service_histories_change_variable = MagicMock()
    # Act
    service_history.add_specified_opening_times_change(current_opening_times, new_opening_times)
    # Assert
    mock_add_change.assert_called_once_with(
        dos_change_key=DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY,
        change=mock_service_histories_change_variable,
    )
    mock_service_histories_change.assert_called_once_with(
        change_key=DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY,
        previous_value=[],
        data={},
    )


def test_service_histories_add_sgsdid_change() -> None:
    # Arrange
    service_history = ServiceHistories(service_id=SERVICE_ID)
    service_history.add_change = mock_add_change = MagicMock()
    sgsdid = "123=456"
    # Act
    service_history.add_sgsdid_change(sgsdid, True)
    # Assert
    mock_add_change.assert_called_once_with(
        dos_change_key=DOS_SGSDID_CHANGE_KEY,
        change=ServiceHistoriesChange(
            data={"add": ["123=456"]},
            previous_value="",
            change_key="cmssgsdid",
            area="clinical",
        ),
    )


def test_service_histories_get_formatted_specified_opening_times() -> None:
    # Arrange
    service_history = ServiceHistories(service_id=SERVICE_ID)
    open_periods = [
        OpenPeriod(time(1, 0, 0), time(2, 0, 0)),
        OpenPeriod(time(3, 0, 0), time(5, 0, 0)),
        OpenPeriod(time(8, 0, 0), time(12, 0, 0)),
    ]
    specified_opening_times = [SpecifiedOpeningTime(open_periods, date(2022, 12, 26), True)]
    # Act
    formatted_specified_opening_times = service_history.get_formatted_specified_opening_times(
        opening_times=specified_opening_times,
    )
    # Assert
    assert [
        "2022-12-26-3600-7200",
        "2022-12-26-10800-18000",
        "2022-12-26-28800-43200",
    ] == formatted_specified_opening_times


@patch(f"{FILE_PATH}.datetime")
@patch(f"{FILE_PATH}.query_dos_db")
def test_service_histories_save_service_histories_insert(
    mock_query_dos_db: MagicMock, mock_datetime: MagicMock
) -> None:
    # Arrange
    mock_connection = MagicMock()
    mock_datetime.now.return_value.strftime.return_value = "2022-12-26 12:00:00"
    service_history = ServiceHistories(service_id=SERVICE_ID)
    service_history.existing_service_history = {}
    service_history.history_already_exists = False
    service_history.service_history = {
        service_history.NEW_CHANGE_KEY: {
            "new": {
                "postaladdress": {
                    "changetype": "modify",
                    "data": "52 Green Lane$Southgate",
                    "area": "demographic",
                    "previous": "51 Green Lane$Southgate",
                },
            },
            "initiator": {"userid": "DOS_INTEGRATION", "timestamp": "TBD"},
            "approver": {"userid": "DOS_INTEGRATION", "timestamp": "TBD"},
        },
    }
    # Act
    service_history.save_service_histories(mock_connection)
    # Assert
    assert mock_query_dos_db.call_count == 2


@patch(f"{FILE_PATH}.datetime")
@patch(f"{FILE_PATH}.query_dos_db")
def test_service_histories_save_service_histories_update(
    mock_query_dos_db: MagicMock, mock_datetime: MagicMock
) -> None:
    # Arrange
    mock_connection = MagicMock()
    mock_datetime.now.return_value.strftime.return_value = "2022-12-26 12:00:00"
    service_history = ServiceHistories(service_id=SERVICE_ID)
    service_history.existing_service_history = {}
    service_history.history_already_exists = True
    service_history.service_history = {
        service_history.NEW_CHANGE_KEY: {
            "new": {
                "postaladdress": {
                    "changetype": "modify",
                    "data": "52 Green Lane$Southgate",
                    "area": "demographic",
                    "previous": "51 Green Lane$Southgate",
                },
            },
            "initiator": {"userid": "DOS_INTEGRATION", "timestamp": "TBD"},
            "approver": {"userid": "DOS_INTEGRATION", "timestamp": "TBD"},
        },
    }
    # Act
    service_history.save_service_histories(mock_connection)
    # Assert
    assert mock_query_dos_db.call_count == 2
