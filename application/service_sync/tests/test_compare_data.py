from unittest.mock import MagicMock, call, patch

import pytest

from application.common.constants import (
    DOS_ADDRESS_CHANGE_KEY,
    DOS_EASTING_CHANGE_KEY,
    DOS_NORTHING_CHANGE_KEY,
    DOS_POSTAL_TOWN_CHANGE_KEY,
    DOS_POSTCODE_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_FRIDAY_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_MONDAY_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_SATURDAY_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_SUNDAY_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_THURSDAY_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_TUESDAY_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_WEDNESDAY_CHANGE_KEY,
    DOS_WEBSITE_CHANGE_KEY,
)
from application.common.opening_times import WEEKDAYS
from application.common.tests.conftest import dummy_dos_location
from application.service_sync.changes_to_dos import ChangesToDoS
from application.service_sync.compare_data import (
    check_for_address_and_postcode_for_changes,
    check_for_specified_opening_times_changes,
    check_for_standard_opening_times_day_changes,
    check_palliative_care_for_change,
    check_public_phone_for_change,
    check_website_for_change,
    compare_location_data,
    compare_nhs_uk_and_dos_data,
    compare_opening_times,
    compare_palliative_care,
    compare_website,
    set_up_for_services_table_change,
)
from common.dos_location import DoSLocation

FILE_PATH = "application.service_sync.compare_data"


@patch(f"{FILE_PATH}.compare_opening_times")
@patch(f"{FILE_PATH}.compare_location_data")
@patch(f"{FILE_PATH}.compare_public_phone")
@patch(f"{FILE_PATH}.compare_website")
@patch(f"{FILE_PATH}.ChangesToDoS")
def test_compare_nhs_uk_and_dos_data(
    mock_changes_to_dos: MagicMock,
    mock_compare_website: MagicMock,
    mock_compare_public_phone: MagicMock,
    mock_compare_location_data: MagicMock,
    mock_compare_opening_times: MagicMock,
):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    # Act
    response = compare_nhs_uk_and_dos_data(dos_service, nhs_entity, service_histories)
    # Assert
    mock_changes_to_dos.assert_called_once_with(
        dos_service=dos_service,
        nhs_entity=nhs_entity,
        service_histories=service_histories,
    )
    mock_compare_website.assert_called_once_with(changes_to_dos=mock_changes_to_dos.return_value)
    mock_compare_public_phone.assert_called_once_with(changes_to_dos=mock_compare_website.return_value)
    mock_compare_location_data.assert_called_once_with(changes_to_dos=mock_compare_public_phone.return_value)
    mock_compare_opening_times.assert_called_once_with(changes_to_dos=mock_compare_location_data.return_value)
    assert response == mock_compare_opening_times.return_value


# @patch(f"{FILE_PATH}.validate_website")
# def test_changes_to_dos_compare_and_validate_website_same_value(mock_validate_website: MagicMock):
#     # Arrange
#     # Act
#     # Assert
#     assert True is response


# @patch(f"{FILE_PATH}.validate_website")
# def test_changes_to_dos_compare_and_validate_website_different_value(mock_validate_website: MagicMock):
#     # Arrange
#     # Act
#     # Assert
#     assert False is response

@patch(f"{FILE_PATH}.is_val_none_or_empty")
@patch(f"{FILE_PATH}.format_website")
def test_changes_to_dos_check_website_for_change_remove_website(
    mock_format_website: MagicMock,
    mock_is_val_none_or_empty: MagicMock,
):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    mock_is_val_none_or_empty.side_effect = [True, False]
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    # Act
    response = check_website_for_change(changes=changes_to_dos)
    # Assert
    assert True is response
    mock_format_website.assert_not_called()


@patch(f"{FILE_PATH}.validate_website")
@patch(f"{FILE_PATH}.format_website")
@patch(f"{FILE_PATH}.is_val_none_or_empty")
@patch(f"{FILE_PATH}.format_website")
def test_changes_to_dos_check_website_for_change_add_website(
    mock_format_website: MagicMock,
    mock_is_val_none_or_empty: MagicMock,
    format_website: MagicMock,
    mock_validate_website: MagicMock,
):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    format_website.return_value = nhs_website = "www.example2.com"
    service_histories = MagicMock()
    mock_is_val_none_or_empty.side_effect = [False, False]
    mock_validate_website.return_value = True
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    # Act
    response = check_website_for_change(changes=changes_to_dos)
    # Assert
    assert True is response
    assert dos_service.web == changes_to_dos.current_website
    assert nhs_website == changes_to_dos.new_website
    mock_format_website.assert_not_called()
    mock_validate_website.assert_called_once_with(nhs_entity, nhs_website)


@patch(f"{FILE_PATH}.check_website_for_change")
@patch(f"{FILE_PATH}.set_up_for_services_table_change")
def test_compare_website(mock_set_up_for_services_table_change: MagicMock,
                        mock_check_website_for_change: MagicMock):
    # Arrange
    changes_to_dos = MagicMock()
    mock_check_website_for_change.return_value = True
    # Act
    response = compare_website(changes_to_dos)
    # Assert
    assert response == mock_set_up_for_services_table_change.return_value
    mock_check_website_for_change.assert_called_once_with(changes=changes_to_dos)
    mock_set_up_for_services_table_change.assert_called_once_with(
        changes_to_dos=changes_to_dos,
        change_key=DOS_WEBSITE_CHANGE_KEY,
        new_value=changes_to_dos.new_website,
        previous_value=changes_to_dos.current_website,
        service_table_field_name="web",
    )


@patch(f"{FILE_PATH}.check_website_for_change")
@patch(f"{FILE_PATH}.set_up_for_services_table_change")
def test_compare_website_no_change(mock_set_up_for_services_table_change: MagicMock,
                                mock_check_website_for_change: MagicMock):
    # Arrange
    changes_to_dos = MagicMock()
    mock_check_website_for_change.return_value = False
    # Act
    response = compare_website(changes_to_dos)
    # Assert
    assert response == changes_to_dos
    mock_check_website_for_change.assert_called_once_with(changes=changes_to_dos)
    mock_set_up_for_services_table_change.assert_not_called()


@patch(f"{FILE_PATH}.get_valid_dos_location")
def test_changes_to_dos_check_for_address_and_postcode_for_changes(mock_get_valid_dos_location: MagicMock):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    dummy_dos_location = DoSLocation(id=0, postcode="DUMMY", easting=0, northing=0, postaltown="STUB",
                                    latitude=0, longitude=0)
    mock_get_valid_dos_location.return_value = dummy_dos_location
    # Act
    address_response, postcode_response, dos_location = check_for_address_and_postcode_for_changes(changes_to_dos)
    # Assert
    assert True is address_response
    assert True is postcode_response
    assert None is not changes_to_dos.new_address
    assert None is not changes_to_dos.new_postcode
    assert None is not changes_to_dos.current_address
    assert None is not changes_to_dos.current_postcode
    mock_get_valid_dos_location.assert_called_once()
    assert dummy_dos_location == dos_location


@patch(f"{FILE_PATH}.log_invalid_nhsuk_postcode")
@patch(f"{FILE_PATH}.get_valid_dos_location")
def test_changes_to_dos_check_for_address_and_postcode_for_changes_postcode_invalid(
    mock_get_valid_dos_location: MagicMock,
    mock_log_invalid_nhsuk_postcode: MagicMock,
):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    mock_get_valid_dos_location.return_value = None
    # Act
    address_response, postcode_response, dos_location = check_for_address_and_postcode_for_changes(changes_to_dos)
    # Assert
    assert False is address_response
    assert False is postcode_response
    assert None is changes_to_dos.new_address
    assert None is changes_to_dos.new_postcode
    assert None is changes_to_dos.current_address
    assert None is changes_to_dos.current_postcode
    mock_get_valid_dos_location.assert_called_once()
    assert mock_get_valid_dos_location.return_value == dos_location

@patch(f"{FILE_PATH}.check_for_address_and_postcode_for_changes")
@patch(f"{FILE_PATH}.set_up_for_services_table_change")
def test_compare_location_data(mock_set_up_for_services_table_change: MagicMock,
                            mock_check_for_address_and_postcode_for_changes: MagicMock):
    # Arrange
    changes_to_dos = MagicMock()
    dos_location = dummy_dos_location()
    mock_check_for_address_and_postcode_for_changes.return_value = [True, True, dos_location]
    # Act
    response = compare_location_data(changes_to_dos)
    # Assert
    assert response == mock_set_up_for_services_table_change.return_value
    mock_check_for_address_and_postcode_for_changes.assert_called_once_with(changes=changes_to_dos)
    mock_set_up_for_services_table_change.assert_has_calls(
        calls=[
            call(
                changes_to_dos=changes_to_dos,
                change_key=DOS_ADDRESS_CHANGE_KEY,
                new_value=changes_to_dos.new_address,
                previous_value=changes_to_dos.current_address,
                service_table_field_name="address",
            ),
            call(
                changes_to_dos=mock_set_up_for_services_table_change.return_value,
                change_key=DOS_POSTCODE_CHANGE_KEY,
                new_value=mock_set_up_for_services_table_change.return_value.new_postcode,
                previous_value=mock_set_up_for_services_table_change.return_value.current_postcode,
                service_table_field_name="postcode",
            ),
            call(
                changes_to_dos=mock_set_up_for_services_table_change.return_value,
                change_key=DOS_POSTAL_TOWN_CHANGE_KEY,
                new_value=dos_location.postaltown,
                previous_value=mock_set_up_for_services_table_change.return_value.dos_service.town,
                service_table_field_name="town",
            ),
            call(
                changes_to_dos=mock_set_up_for_services_table_change.return_value,
                change_key=DOS_EASTING_CHANGE_KEY,
                new_value=dos_location.easting,
                previous_value=mock_set_up_for_services_table_change.return_value.dos_service.easting,
                service_table_field_name="easting",
            ),
            call(
                changes_to_dos=mock_set_up_for_services_table_change.return_value,
                change_key=DOS_NORTHING_CHANGE_KEY,
                new_value=dos_location.northing,
                previous_value=mock_set_up_for_services_table_change.return_value.dos_service.northing,
                service_table_field_name="northing",
            ),
            call(
                changes_to_dos=mock_set_up_for_services_table_change.return_value,
                change_key="latitude",
                new_value=dos_location.latitude,
                previous_value=mock_set_up_for_services_table_change.return_value.dos_service.latitude,
                service_table_field_name="latitude",
                update_service_history=False,
            ),
            call(
                changes_to_dos=mock_set_up_for_services_table_change.return_value,
                change_key="longitude",
                new_value=dos_location.longitude,
                previous_value=mock_set_up_for_services_table_change.return_value.dos_service.longitude,
                service_table_field_name="longitude",
                update_service_history=False,
            ),
            call().__eq__(mock_set_up_for_services_table_change.return_value),
        ],
    )

@patch(f"{FILE_PATH}.check_for_address_and_postcode_for_changes")
@patch(f"{FILE_PATH}.set_up_for_services_table_change")
def test_compare_location_data_no_changes(mock_set_up_for_services_table_change: MagicMock,
                                        mock_check_for_address_and_postcode_for_changes: MagicMock):
    # Arrange
    changes_to_dos = MagicMock()
    mock_check_for_address_and_postcode_for_changes.return_value = False, False, None
    # Act
    response = compare_location_data(changes_to_dos)
    # Assert
    assert response == changes_to_dos
    mock_check_for_address_and_postcode_for_changes.assert_called_once_with(changes=changes_to_dos)
    mock_set_up_for_services_table_change.assert_not_called()

@pytest.mark.parametrize("weekday", WEEKDAYS)
def test_changes_to_dos_check_for_standard_opening_times_day_changes(weekday: str):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    dos_service.standard_opening_times.same_openings.return_value = False
    # Act
    check_for_standard_opening_times_day_changes(changes_to_dos,weekday)
    # Assert
    assert hasattr(changes_to_dos, f"current_{weekday}_opening_times")
    assert hasattr(changes_to_dos, f"new_{weekday}_opening_times")


@pytest.mark.parametrize("weekday", WEEKDAYS)
def test_changes_to_dos_check_for_standard_opening_times_day_changes_no_changes(weekday: str):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    dos_service.standard_opening_times.same_openings.return_value = True
    # Act
    check_for_standard_opening_times_day_changes(changes_to_dos, weekday)
    # Assert
    assert False is hasattr(changes_to_dos, f"current_{weekday}_opening_times")
    assert False is hasattr(changes_to_dos, f"new_{weekday}_opening_times")

@patch(f"{FILE_PATH}.SpecifiedOpeningTime")
def test_changes_to_dos_check_for_specified_opening_times_changes(mock_specified_opening_time: MagicMock):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    mock_specified_opening_time.equal_lists.return_value = False
    mock_specified_opening_time.remove_past_dates.return_value = ["2020-01-01"]
    # Act
    response = check_for_specified_opening_times_changes(changes=changes_to_dos)
    # Assert
    assert True is response
    assert None is not changes_to_dos.new_specified_opening_times
    assert None is not changes_to_dos.current_specified_opening_times


@patch(f"{FILE_PATH}.SpecifiedOpeningTime")
def test_changes_to_dos_check_for_specified_opening_times_changes_no_change(mock_specified_opening_time: MagicMock):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    mock_specified_opening_time.equal_lists.return_value = True
    # Act
    response = check_for_specified_opening_times_changes(changes=changes_to_dos)
    # Assert
    assert False is response
    assert None is changes_to_dos.new_specified_opening_times
    assert None is changes_to_dos.current_specified_opening_times

@patch(f"{FILE_PATH}.check_for_specified_opening_times_changes")
@patch(f"{FILE_PATH}.check_for_standard_opening_times_day_changes")
@patch(f"{FILE_PATH}.set_up_for_services_table_change")
@patch(f"{FILE_PATH}.validate_opening_times")
def test_compare_opening_times(
    mock_validate_opening_times: MagicMock,
    mock_set_up_for_services_table_change: MagicMock,
    mock_check_for_standard_opening_times_day_changes: MagicMock,
    mock_check_for_specified_opening_times_changes: MagicMock,
):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    changes_to_dos.new_monday_opening_times = "new_monday_opening_times"
    changes_to_dos.new_tuesday_opening_times = "new_tuesday_opening_times"
    changes_to_dos.new_wednesday_opening_times = "new_wednesday_opening_times"
    changes_to_dos.new_thursday_opening_times = "new_thursday_opening_times"
    changes_to_dos.new_friday_opening_times = "new_friday_opening_times"
    changes_to_dos.new_saturday_opening_times = "new_saturday_opening_times"
    changes_to_dos.new_sunday_opening_times = "new_sunday_opening_times"
    mock_validate_opening_times.return_value = True
    dos_service.standard_opening_times.same_openings.return_value = False
    mock_check_for_standard_opening_times_day_changes.return_value = True
    mock_check_for_specified_opening_times_changes.return_value = True
    # Act
    response = compare_opening_times(changes_to_dos)
    # Assert
    assert response == changes_to_dos
    changes_to_dos.service_histories.add_standard_opening_times_change.assert_has_calls(
        calls=[
            call(
                current_opening_times=changes_to_dos.dos_service.standard_opening_times,
                new_opening_times=changes_to_dos.nhs_entity.standard_opening_times,
                dos_weekday_change_key=DOS_STANDARD_OPENING_TIMES_MONDAY_CHANGE_KEY,
                weekday="monday",
            ),
            call(
                current_opening_times=changes_to_dos.dos_service.standard_opening_times,
                new_opening_times=changes_to_dos.nhs_entity.standard_opening_times,
                dos_weekday_change_key=DOS_STANDARD_OPENING_TIMES_TUESDAY_CHANGE_KEY,
                weekday="tuesday",
            ),
            call(
                current_opening_times=changes_to_dos.dos_service.standard_opening_times,
                new_opening_times=changes_to_dos.nhs_entity.standard_opening_times,
                dos_weekday_change_key=DOS_STANDARD_OPENING_TIMES_WEDNESDAY_CHANGE_KEY,
                weekday="wednesday",
            ),
            call(
                current_opening_times=changes_to_dos.dos_service.standard_opening_times,
                new_opening_times=changes_to_dos.nhs_entity.standard_opening_times,
                dos_weekday_change_key=DOS_STANDARD_OPENING_TIMES_THURSDAY_CHANGE_KEY,
                weekday="thursday",
            ),
            call(
                current_opening_times=changes_to_dos.dos_service.standard_opening_times,
                new_opening_times=changes_to_dos.nhs_entity.standard_opening_times,
                dos_weekday_change_key=DOS_STANDARD_OPENING_TIMES_FRIDAY_CHANGE_KEY,
                weekday="friday",
            ),
            call(
                current_opening_times=changes_to_dos.dos_service.standard_opening_times,
                new_opening_times=changes_to_dos.nhs_entity.standard_opening_times,
                dos_weekday_change_key=DOS_STANDARD_OPENING_TIMES_SATURDAY_CHANGE_KEY,
                weekday="saturday",
            ),
            call(
                current_opening_times=changes_to_dos.dos_service.standard_opening_times,
                new_opening_times=changes_to_dos.nhs_entity.standard_opening_times,
                dos_weekday_change_key=DOS_STANDARD_OPENING_TIMES_SUNDAY_CHANGE_KEY,
                weekday="sunday",
            ),
        ],
    )
    changes_to_dos.service_histories.add_specified_opening_times_change.assert_called_once_with(
        current_opening_times=None,
        new_opening_times=None,
    )


@patch(f"{FILE_PATH}.validate_opening_times")
def test_compare_opening_times_invalid_opening_times(
    mock_validate_opening_times: MagicMock,
):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    mock_validate_opening_times.return_value = False
    changes_to_dos.nhs_entity.standard_opening_times.fully_closed.return_value = False
    # Act
    response = compare_opening_times(changes_to_dos)
    # Assert
    assert response == changes_to_dos
    changes_to_dos.service_histories.add_standard_opening_times_change.assert_not_called()
    changes_to_dos.service_histories.add_specified_opening_times_change.assert_not_called()


@patch(f"{FILE_PATH}.validate_opening_times")
def test_compare_opening_times_blank_opening_times(
    mock_validate_opening_times: MagicMock,
):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    changes_to_dos.nhs_entity.standard_opening_times.fully_closed.return_value = True
    mock_validate_opening_times.return_value = False
    # Act
    response = compare_opening_times(changes_to_dos)
    # Assert
    assert response == changes_to_dos
    changes_to_dos.service_histories.add_standard_opening_times_change.assert_not_called()
    changes_to_dos.service_histories.add_specified_opening_times_change.assert_not_called()


@patch(f"{FILE_PATH}.check_for_specified_opening_times_changes")
@patch(f"{FILE_PATH}.check_for_standard_opening_times_day_changes")
@patch(f"{FILE_PATH}.set_up_for_services_table_change")
@patch(f"{FILE_PATH}.validate_opening_times")
def test_compare_opening_times_no_change(
    mock_validate_opening_times: MagicMock,
    mock_set_up_for_services_table_change: MagicMock,
    mock_check_for_standard_opening_times_day_changes: MagicMock,
    mock_check_for_specified_opening_times_changes: MagicMock,
):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    changes_to_dos.new_monday_opening_times = "new_monday_opening_times"
    changes_to_dos.new_tuesday_opening_times = "new_tuesday_opening_times"
    changes_to_dos.new_wednesday_opening_times = "new_wednesday_opening_times"
    changes_to_dos.new_thursday_opening_times = "new_thursday_opening_times"
    changes_to_dos.new_friday_opening_times = "new_friday_opening_times"
    changes_to_dos.new_saturday_opening_times = "new_saturday_opening_times"
    changes_to_dos.new_sunday_opening_times = "new_sunday_opening_times"
    mock_validate_opening_times.return_value = True
    dos_service.standard_opening_times.same_openings.return_value = False
    mock_check_for_standard_opening_times_day_changes.return_value = False
    mock_check_for_specified_opening_times_changes.return_value = False
    # Act
    response = compare_opening_times(changes_to_dos)
    # Assert
    assert response == changes_to_dos
    changes_to_dos.service_histories.add_standard_opening_times_change.assert_not_called()
    changes_to_dos.service_histories.add_specified_opening_times_change.assert_not_called()


@patch(f"{FILE_PATH}.ServiceHistoriesChange")
def test_set_up_for_services_table_change(mock_service_histories_change: MagicMock):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    change_key = "change_key"
    new_value = "new_value"
    previous_value = "previous_value"
    service_table_field_name = "service_table_field_name"
    # Act
    response = set_up_for_services_table_change(
        changes_to_dos=changes_to_dos,
        change_key=change_key,
        new_value=new_value,
        previous_value=previous_value,
        service_table_field_name=service_table_field_name,
        update_service_history=True,
    )
    # Assert
    assert response == changes_to_dos
    assert changes_to_dos.demographic_changes == {service_table_field_name: new_value}
    mock_service_histories_change.assert_called_once_with(
        data=new_value,
        previous_value=previous_value,
        change_key=change_key,
    )
    changes_to_dos.service_histories.add_change.assert_called_once_with(
        dos_change_key=change_key,
        change=mock_service_histories_change.return_value,
    )


@patch(f"{FILE_PATH}.ServiceHistoriesChange")
def test_set_up_for_services_table_change_no_service_history_update(mock_service_histories_change: MagicMock):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    change_key = "change_key"
    new_value = "new_value"
    previous_value = "previous_value"
    service_table_field_name = "service_table_field_name"
    # Act
    response = set_up_for_services_table_change(
        changes_to_dos=changes_to_dos,
        change_key=change_key,
        new_value=new_value,
        previous_value=previous_value,
        service_table_field_name=service_table_field_name,
        update_service_history=False,
    )
    # Assert
    assert response == changes_to_dos
    assert changes_to_dos.demographic_changes == {service_table_field_name: new_value}
    mock_service_histories_change.assert_not_called()
    changes_to_dos.service_histories.add_change.assert_not_called()


def test_changes_to_dos_check_public_phone_for_change():
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    dos_service.publicphone = "0123456789"
    nhs_entity.publicphone = "012345678"
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    # Act
    response = check_public_phone_for_change(changes=changes_to_dos)
    # Assert
    assert True is response


def test_changes_to_dos_check_public_phone_for_change_no_change():
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    dos_service.publicphone = "0123456789"
    nhs_entity.phone = "0123456789"
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    # Act
    response = check_public_phone_for_change(changes=changes_to_dos)
    # Assert
    assert False is response

#TODO add test cover functions that uses check_public_phone_for_change

def test_changes_to_dos_check_palliative_care_for_change():
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    dos_service.palliative_care = True
    nhs_entity.palliative_care = False
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    # Act
    response = check_palliative_care_for_change(changes=changes_to_dos)
    # Assert
    assert True is response


def test_changes_to_dos_check_palliative_care_for_change_no_change():
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    dos_service.palliative_care = False
    nhs_entity.palliative_care = False
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    # Act
    response = check_palliative_care_for_change(changes=changes_to_dos)
    # Assert
    assert False is response


@patch(f"{FILE_PATH}.log_incorrect_palliative_stockholder_type")
@patch(f"{FILE_PATH}.log_palliative_care_not_equal")
def test_compare_palliative_care_unequal(
    mock_log_palliative_care_not_equal: MagicMock,
    mock_log_incorrect_palliative_stockholder_type: MagicMock,
):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    dos_service.typeid = 13
    dos_service.palliative_care = dos_palliative_care = True
    nhs_entity.palliative_care = nhs_palliative_care = False
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)

    # Act
    response = compare_palliative_care(changes_to_dos)
    # Assert
    assert response == changes_to_dos
    mock_log_palliative_care_not_equal.assert_called_once_with(
        nhs_uk_palliative_care=nhs_palliative_care,
        dos_palliative_care=dos_palliative_care,
    )
    mock_log_incorrect_palliative_stockholder_type.assert_not_called()


@patch(f"{FILE_PATH}.get_palliative_care_log_value")
@patch(f"{FILE_PATH}.log_incorrect_palliative_stockholder_type")
@patch(f"{FILE_PATH}.log_palliative_care_not_equal")
def test_compare_palliative_care_invalid(
    mock_log_palliative_care_not_equal: MagicMock,
    mock_log_incorrect_palliative_stockholder_type: MagicMock,
    mock_get_palliative_care_log_value: MagicMock,
):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    dos_service.typeid = 131
    dos_service.palliative_care = dos_palliative_care = True
    nhs_entity.palliative_care = nhs_palliative_care = False
    mock_get_palliative_care_log_value.return_value = nhs_palliative_care
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)

    # Act
    response = compare_palliative_care(changes_to_dos)
    # Assert
    assert response == changes_to_dos
    mock_log_palliative_care_not_equal.assert_not_called()
    mock_log_incorrect_palliative_stockholder_type.assert_called_once_with(
        nhs_uk_palliative_care=nhs_palliative_care,
        dos_palliative_care=dos_palliative_care,
        dos_service=dos_service,
    )
