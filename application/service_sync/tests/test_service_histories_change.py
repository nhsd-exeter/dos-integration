from unittest.mock import patch

from pytest import mark, raises

from ..service_histories_change import ServiceHistoriesChange
from common.constants import (
    DOS_DEMOGRAPHICS_CHANGE_TYPE,
    DOS_SERVICES_TABLE_CHANGE_TYPE_LIST,
    DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_FRIDAY_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_MONDAY_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_SATURDAY_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_SUNDAY_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_THURSDAY_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_TUESDAY_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_WEDNESDAY_CHANGE_KEY,
    DOS_WEBSITE_CHANGE_KEY,
)

FILE_PATH = "application.service_sync.service_histories_change"
DATA = "New value to be added to db"
PREVIOUS_VALUE = "Old value to be removed from db"


@mark.parametrize("demographics_change_key", (DOS_SERVICES_TABLE_CHANGE_TYPE_LIST))
@patch(f"{FILE_PATH}.ServiceHistoriesChange.get_demographics_change_action")
def test_service_histories_change_demographics_change(mock_get_demographics_change_action, demographics_change_key):
    # Act
    service_histories_change = ServiceHistoriesChange(
        data=DATA, previous_value=PREVIOUS_VALUE, change_key=demographics_change_key
    )
    # Assert
    assert DATA == service_histories_change.data
    assert PREVIOUS_VALUE == service_histories_change.previous_value
    assert DOS_DEMOGRAPHICS_CHANGE_TYPE == service_histories_change.area
    mock_get_demographics_change_action.assert_called_once_with()


@mark.parametrize(
    "opening_times_change_key",
    [
        DOS_STANDARD_OPENING_TIMES_MONDAY_CHANGE_KEY,
        DOS_STANDARD_OPENING_TIMES_TUESDAY_CHANGE_KEY,
        DOS_STANDARD_OPENING_TIMES_WEDNESDAY_CHANGE_KEY,
        DOS_STANDARD_OPENING_TIMES_THURSDAY_CHANGE_KEY,
        DOS_STANDARD_OPENING_TIMES_FRIDAY_CHANGE_KEY,
        DOS_STANDARD_OPENING_TIMES_SATURDAY_CHANGE_KEY,
        DOS_STANDARD_OPENING_TIMES_SUNDAY_CHANGE_KEY,
        DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY,
    ],
)
@patch(f"{FILE_PATH}.ServiceHistoriesChange.get_opening_times_change_action")
def test_service_histories_change_opening_times_change(mock_get_opening_times_change_action, opening_times_change_key):
    # Act
    service_histories_change = ServiceHistoriesChange(
        data=DATA, previous_value=PREVIOUS_VALUE, change_key=opening_times_change_key
    )
    # Assert
    assert DATA == service_histories_change.data
    assert PREVIOUS_VALUE == service_histories_change.previous_value
    assert DOS_DEMOGRAPHICS_CHANGE_TYPE == service_histories_change.area
    mock_get_opening_times_change_action.assert_called_once_with()


@patch(f"{FILE_PATH}.ServiceHistoriesChange.get_opening_times_change_action")
@patch(f"{FILE_PATH}.ServiceHistoriesChange.get_demographics_change_action")
def test_service_histories_change_no_change(demographics_change_key, mock_get_opening_times_change_action):
    # Act
    with raises(ValueError, match="Unknown change key"):
        ServiceHistoriesChange(data=DATA, previous_value=PREVIOUS_VALUE, change_key="ANY")
    # Assert
    demographics_change_key.assert_not_called()
    mock_get_opening_times_change_action.assert_not_called()


@mark.parametrize(
    "data, previous_value, expected_action",
    [(DATA, PREVIOUS_VALUE, "modify"), (None, PREVIOUS_VALUE, "delete"), (DATA, None, "add")],
)
def test_service_histories_change_get_demographics_change_action(data, previous_value, expected_action):
    # Act
    service_histories_change = ServiceHistoriesChange(
        data=data, previous_value=previous_value, change_key=DOS_WEBSITE_CHANGE_KEY
    )  # get_demographics_change_action should be called by __init__ function
    # Assert
    assert expected_action == service_histories_change.change_action


@mark.parametrize(
    "data, expected_action",
    [
        ({"remove": "TO_REMOVE", "add": "TO_ADD"}, "modify"),
        ({"remove": "TO_REMOVE"}, "delete"),
        ({"add": "TO_ADD"}, "add"),
    ],
)
def test_service_histories_change_get_opening_times_change_action(data, expected_action):
    # Act
    service_histories_change = ServiceHistoriesChange(
        data=data, previous_value=None, change_key=DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY
    )  # get_opening_times_change_action should be called by __init__ function
    # Assert
    assert expected_action == service_histories_change.change_action


def test_service_histories_change_get_opening_times_change_action_error():
    # Act & Assert
    with raises(ValueError, match="Unknown change action"):
        ServiceHistoriesChange(data={}, previous_value=None, change_key=DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY)


@patch(f"{FILE_PATH}.ServiceHistoriesChange.get_demographics_change_action")
def test_service_histories_change_get_change(mock_get_demographics_change_action):
    # Arrange
    mock_get_demographics_change_action.return_value = change_action = "Change Action"
    service_histories_change = ServiceHistoriesChange(
        data=DATA, previous_value=PREVIOUS_VALUE, change_key=DOS_WEBSITE_CHANGE_KEY
    )
    # Act
    response = service_histories_change.get_change()
    # Assert
    assert {
        "changetype": change_action,
        "data": DATA,
        "area": DOS_DEMOGRAPHICS_CHANGE_TYPE,
        "previous": PREVIOUS_VALUE,
    } == response


@patch(f"{FILE_PATH}.ServiceHistoriesChange.get_demographics_change_action")
def test_service_histories_change_get_change_add(mock_get_demographics_change_action):
    # Arrange
    mock_get_demographics_change_action.return_value = change_action = "add"
    service_histories_change = ServiceHistoriesChange(
        data=DATA, previous_value=PREVIOUS_VALUE, change_key=DOS_WEBSITE_CHANGE_KEY
    )
    # Act
    response = service_histories_change.get_change()
    # Assert
    assert {
        "changetype": change_action,
        "data": DATA,
        "area": DOS_DEMOGRAPHICS_CHANGE_TYPE,
    } == response
