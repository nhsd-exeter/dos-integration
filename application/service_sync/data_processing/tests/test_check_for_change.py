from unittest.mock import MagicMock, call, patch

from application.common.constants import (
    DOS_ACTIVE_STATUS_ID,
    DOS_ADDRESS_CHANGE_KEY,
    DOS_CLOSED_STATUS_ID,
    DOS_EASTING_CHANGE_KEY,
    DOS_NORTHING_CHANGE_KEY,
    DOS_POSTAL_TOWN_CHANGE_KEY,
    DOS_POSTCODE_CHANGE_KEY,
    DOS_PUBLIC_PHONE_CHANGE_KEY,
    DOS_SERVICE_HISTORY_ACTIVE_STATUS,
    DOS_SERVICE_HISTORY_CLOSED_STATUS,
    DOS_STANDARD_OPENING_TIMES_FRIDAY_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_MONDAY_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_SATURDAY_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_SUNDAY_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_THURSDAY_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_TUESDAY_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_WEDNESDAY_CHANGE_KEY,
    DOS_STATUS_CHANGE_KEY,
    DOS_WEBSITE_CHANGE_KEY,
)
from application.conftest import dummy_dos_location
from application.service_sync.data_processing.changes_to_dos import ChangesToDoS
from application.service_sync.data_processing.check_for_change import (
    check_blood_pressure_for_change,
    check_contraception_for_change,
    check_location_for_change,
    check_opening_times_for_changes,
    check_palliative_care_for_change,
    check_public_phone_for_change,
    check_website_for_change,
    compare_nhs_uk_and_dos_data,
    services_change,
    status_id_change,
)

FILE_PATH = "application.service_sync.data_processing.check_for_change"


@patch(f"{FILE_PATH}.check_contraception_for_change")
@patch(f"{FILE_PATH}.check_blood_pressure_for_change")
@patch(f"{FILE_PATH}.check_palliative_care_for_change")
@patch(f"{FILE_PATH}.check_opening_times_for_changes")
@patch(f"{FILE_PATH}.check_location_for_change")
@patch(f"{FILE_PATH}.check_public_phone_for_change")
@patch(f"{FILE_PATH}.check_website_for_change")
@patch(f"{FILE_PATH}.ChangesToDoS")
def test_compare_nhs_uk_and_dos_data(
    mock_changes_to_dos: MagicMock,
    mock_check_website_for_change: MagicMock,
    mock_check_public_phone_for_change: MagicMock,
    mock_check_location_for_change: MagicMock,
    mock_check_opening_times_for_changes: MagicMock,
    mock_check_palliative_care_for_change: MagicMock,
    mock_check_blood_pressure_for_change: MagicMock,
    mock_check_contraception_for_change: MagicMock,
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
    mock_check_website_for_change.assert_called_once_with(changes_to_dos=mock_changes_to_dos.return_value)
    mock_check_public_phone_for_change.assert_called_once_with(
        changes_to_dos=mock_check_website_for_change.return_value,
    )
    mock_check_location_for_change.assert_called_once_with(
        changes_to_dos=mock_check_public_phone_for_change.return_value,
    )
    mock_check_opening_times_for_changes.assert_called_once_with(
        changes_to_dos=mock_check_location_for_change.return_value,
    )
    mock_check_palliative_care_for_change.assert_called_once_with(
        changes_to_dos=mock_check_opening_times_for_changes.return_value,
    )
    mock_check_blood_pressure_for_change.assert_called_once_with(
        changes_to_dos=mock_check_palliative_care_for_change.return_value,
    )
    mock_check_contraception_for_change.assert_called_once_with(
        changes_to_dos=mock_check_blood_pressure_for_change.return_value,
    )
    assert response == mock_check_contraception_for_change.return_value


@patch(f"{FILE_PATH}.compare_website")
@patch(f"{FILE_PATH}.services_change")
def test_check_website_for_change(mock_services_change: MagicMock, mock_compare_website: MagicMock):
    # Arrange
    changes_to_dos = MagicMock()
    mock_compare_website.return_value = True
    # Act
    response = check_website_for_change(changes_to_dos)
    # Assert
    assert response == mock_services_change.return_value
    mock_compare_website.assert_called_once_with(changes=changes_to_dos)
    mock_services_change.assert_called_once_with(
        changes_to_dos=changes_to_dos,
        change_key=DOS_WEBSITE_CHANGE_KEY,
        new_value=changes_to_dos.new_website,
        previous_value=changes_to_dos.current_website,
        service_table_field_name="web",
    )


@patch(f"{FILE_PATH}.compare_website")
@patch(f"{FILE_PATH}.services_change")
def test_check_website_for_change_no_change(
    mock_services_change: MagicMock,
    mock_compare_website: MagicMock,
):
    # Arrange
    changes_to_dos = MagicMock()
    mock_compare_website.return_value = False
    # Act
    response = check_website_for_change(changes_to_dos)
    # Assert
    assert response == changes_to_dos
    mock_compare_website.assert_called_once_with(changes=changes_to_dos)
    mock_services_change.assert_not_called()


@patch(f"{FILE_PATH}.compare_location")
@patch(f"{FILE_PATH}.services_change")
def test_check_location_for_change(mock_services_change: MagicMock, mock_compare_location: MagicMock):
    # Arrange
    changes_to_dos = MagicMock()
    dos_location = dummy_dos_location()
    mock_compare_location.return_value = [True, True, dos_location]
    # Act
    response = check_location_for_change(changes_to_dos)
    # Assert
    assert response == mock_services_change.return_value
    mock_compare_location.assert_called_once_with(changes=changes_to_dos)
    mock_services_change.assert_has_calls(
        calls=[
            call(
                changes_to_dos=changes_to_dos,
                change_key=DOS_ADDRESS_CHANGE_KEY,
                new_value=changes_to_dos.new_address,
                previous_value=changes_to_dos.current_address,
                service_table_field_name="address",
            ),
            call(
                changes_to_dos=mock_services_change.return_value,
                change_key=DOS_POSTCODE_CHANGE_KEY,
                new_value=mock_services_change.return_value.new_postcode,
                previous_value=mock_services_change.return_value.current_postcode,
                service_table_field_name="postcode",
            ),
            call(
                changes_to_dos=mock_services_change.return_value,
                change_key=DOS_POSTAL_TOWN_CHANGE_KEY,
                new_value=dos_location.postaltown,
                previous_value=mock_services_change.return_value.dos_service.town,
                service_table_field_name="town",
            ),
            call(
                changes_to_dos=mock_services_change.return_value,
                change_key=DOS_EASTING_CHANGE_KEY,
                new_value=dos_location.easting,
                previous_value=mock_services_change.return_value.dos_service.easting,
                service_table_field_name="easting",
            ),
            call(
                changes_to_dos=mock_services_change.return_value,
                change_key=DOS_NORTHING_CHANGE_KEY,
                new_value=dos_location.northing,
                previous_value=mock_services_change.return_value.dos_service.northing,
                service_table_field_name="northing",
            ),
            call(
                changes_to_dos=mock_services_change.return_value,
                change_key="latitude",
                new_value=dos_location.latitude,
                previous_value=mock_services_change.return_value.dos_service.latitude,
                service_table_field_name="latitude",
                update_service_history=False,
            ),
            call(
                changes_to_dos=mock_services_change.return_value,
                change_key="longitude",
                new_value=dos_location.longitude,
                previous_value=mock_services_change.return_value.dos_service.longitude,
                service_table_field_name="longitude",
                update_service_history=False,
            ),
            call().__eq__(mock_services_change.return_value),
        ],
    )


@patch(f"{FILE_PATH}.compare_location")
@patch(f"{FILE_PATH}.services_change")
def test_check_location_for_change_no_changes(
    mock_services_change: MagicMock,
    mock_compare_location: MagicMock,
):
    # Arrange
    changes_to_dos = MagicMock()
    mock_compare_location.return_value = False, False, None
    # Act
    response = check_location_for_change(changes_to_dos)
    # Assert
    assert response == changes_to_dos
    mock_compare_location.assert_called_once_with(changes=changes_to_dos)
    mock_services_change.assert_not_called()


@patch(f"{FILE_PATH}.compare_specified_opening_times")
@patch(f"{FILE_PATH}.compare_standard_opening_times")
@patch(f"{FILE_PATH}.services_change")
@patch(f"{FILE_PATH}.validate_opening_times")
def test_check_opening_times_for_changes(
    mock_validate_opening_times: MagicMock,
    mock_services_change: MagicMock,
    mock_compare_standard_opening_times: MagicMock,
    mock_compare_specified_opening_times: MagicMock,
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
    mock_compare_standard_opening_times.return_value = True
    mock_compare_specified_opening_times.return_value = True
    # Act
    response = check_opening_times_for_changes(changes_to_dos)
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
def test_check_opening_times_for_changes_invalid_opening_times(
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
    response = check_opening_times_for_changes(changes_to_dos)
    # Assert
    assert response == changes_to_dos
    changes_to_dos.service_histories.add_standard_opening_times_change.assert_not_called()
    changes_to_dos.service_histories.add_specified_opening_times_change.assert_not_called()


@patch(f"{FILE_PATH}.validate_opening_times")
def test_check_opening_times_for_changes_blank_opening_times(
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
    response = check_opening_times_for_changes(changes_to_dos)
    # Assert
    assert response == changes_to_dos
    changes_to_dos.service_histories.add_standard_opening_times_change.assert_not_called()
    changes_to_dos.service_histories.add_specified_opening_times_change.assert_not_called()


@patch(f"{FILE_PATH}.compare_specified_opening_times")
@patch(f"{FILE_PATH}.compare_standard_opening_times")
@patch(f"{FILE_PATH}.services_change")
@patch(f"{FILE_PATH}.validate_opening_times")
def test_check_opening_times_for_changes_no_change(
    mock_validate_opening_times: MagicMock,
    mock_services_change: MagicMock,
    mock_compare_standard_opening_times: MagicMock,
    mock_compare_specified_opening_times: MagicMock,
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
    mock_compare_standard_opening_times.return_value = False
    mock_compare_specified_opening_times.return_value = False
    # Act
    response = check_opening_times_for_changes(changes_to_dos)
    # Assert
    assert response == changes_to_dos
    changes_to_dos.service_histories.add_standard_opening_times_change.assert_not_called()
    changes_to_dos.service_histories.add_specified_opening_times_change.assert_not_called()


@patch(f"{FILE_PATH}.services_change")
@patch(f"{FILE_PATH}.compare_public_phone")
def test_check_public_phone_for_change_change(
    mock_compare_public_phone: MagicMock,
    mock_set_up_for_service_table_change: MagicMock,
):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    dos_service.publicphone = "01234 567890"
    nhs_entity.phone = "08976 543210"
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    changes_to_dos.current_public_phone = dos_service.publicphone
    changes_to_dos.new_public_phone = nhs_entity.phone
    mock_compare_public_phone.return_value = True
    mock_set_up_for_service_table_change.return_value = changes_to_dos
    # Act
    response = check_public_phone_for_change(changes_to_dos)
    # Assert
    mock_compare_public_phone.assert_called_once_with(changes=changes_to_dos)
    mock_set_up_for_service_table_change.assert_called_once_with(
        changes_to_dos=changes_to_dos,
        change_key=DOS_PUBLIC_PHONE_CHANGE_KEY,
        new_value=changes_to_dos.new_public_phone,
        previous_value=changes_to_dos.current_public_phone,
        service_table_field_name="publicphone",
    )
    assert response == changes_to_dos


@patch(f"{FILE_PATH}.services_change")
@patch(f"{FILE_PATH}.compare_public_phone")
def test_check_public_phone_for_change_no_change(
    mock_compare_public_phone: MagicMock,
    mock_set_up_for_service_table_change: MagicMock,
):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    dos_service.publicphone = "01234 567890"
    nhs_entity.phone = "01234 567890"
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    changes_to_dos.current_public_phone = dos_service.publicphone
    changes_to_dos.new_public_phone = nhs_entity.phone
    mock_compare_public_phone.return_value = False
    mock_set_up_for_service_table_change.return_value = changes_to_dos
    # Act
    response = check_public_phone_for_change(changes_to_dos)
    # Assert
    mock_compare_public_phone.assert_called_once_with(changes=changes_to_dos)
    mock_set_up_for_service_table_change.assert_not_called()
    assert response == changes_to_dos


def test_check_palliative_care_for_change_unequal():
    # Arrange
    dos_service = MagicMock()
    dos_service.odscode = "12345"
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    dos_service.typeid = 13
    dos_service.palliative_care = True
    nhs_entity.palliative_care = False
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    # Act
    response = check_palliative_care_for_change(changes_to_dos)
    # Assert
    assert response == changes_to_dos


@patch(f"{FILE_PATH}.get_palliative_care_log_value")
def test_check_palliative_care_for_change_incorrect_odscode_length(
    mock_get_palliative_care_log_value: MagicMock,
):
    # Arrange
    dos_service = MagicMock()
    dos_service.odscode = "123456"
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    dos_service.typeid = 131
    dos_service.palliative_care = True
    nhs_entity.palliative_care = nhs_palliative_care = False
    mock_get_palliative_care_log_value.return_value = nhs_palliative_care
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    # Act
    response = check_palliative_care_for_change(changes_to_dos)
    # Assert
    assert response == changes_to_dos


@patch(f"{FILE_PATH}.status_id_change")
@patch(f"{FILE_PATH}.compare_blood_pressure")
def test_check_blood_pressure_for_change(
    mock_compare_blood_pressure: MagicMock,
    mock_status_id_change: MagicMock,
):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    dos_service.typeid = 148
    dos_service.palliative_care = True
    nhs_entity.palliative_care = False
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    mock_compare_blood_pressure.return_value = True
    # Act
    check_blood_pressure_for_change(changes_to_dos=changes_to_dos)
    # Assert
    mock_compare_blood_pressure.assert_called_once_with(changes=changes_to_dos)
    mock_status_id_change.assert_called_once_with(
        changes_to_dos=changes_to_dos,
        new_value=changes_to_dos.nhs_entity.blood_pressure,
        previous_value=changes_to_dos.dos_service.status_name,
    )


@patch(f"{FILE_PATH}.status_id_change")
@patch(f"{FILE_PATH}.compare_contraception")
def test_check_contraception_for_change(
    mock_compare_contraception: MagicMock,
    mock_status_id_change: MagicMock,
):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    dos_service.typeid = 149
    dos_service.palliative_care = True
    nhs_entity.palliative_care = False
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    mock_compare_contraception.return_value = True
    # Act
    check_contraception_for_change(changes_to_dos=changes_to_dos)
    # Assert
    mock_compare_contraception.assert_called_once_with(changes=changes_to_dos)
    mock_status_id_change.assert_called_once_with(
        changes_to_dos=changes_to_dos,
        new_value=changes_to_dos.nhs_entity.contraception,
        previous_value=changes_to_dos.dos_service.status_name,
    )


@patch(f"{FILE_PATH}.ServiceHistoriesChange")
def test_services_change(mock_service_histories_change: MagicMock):
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
    response = services_change(
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
def test_services_change_no_service_history_update(mock_service_histories_change: MagicMock):
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
    response = services_change(
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


@patch(f"{FILE_PATH}.ServiceHistoriesChange")
def test_status_id_change__active(mock_service_histories_change: MagicMock):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    new_value = True
    previous_value = "previous_value"
    # Act
    response = status_id_change(
        changes_to_dos=changes_to_dos,
        new_value=new_value,
        previous_value=previous_value,
    )
    # Assert
    assert response == changes_to_dos
    assert changes_to_dos.demographic_changes == {"statusid": DOS_ACTIVE_STATUS_ID}
    mock_service_histories_change.assert_called_once_with(
        data=DOS_SERVICE_HISTORY_ACTIVE_STATUS,
        previous_value=previous_value,
        change_key=DOS_STATUS_CHANGE_KEY,
    )
    changes_to_dos.service_histories.add_change.assert_called_once_with(
        dos_change_key=DOS_STATUS_CHANGE_KEY,
        change=mock_service_histories_change.return_value,
    )


@patch(f"{FILE_PATH}.ServiceHistoriesChange")
def test_status_id_change__closed(mock_service_histories_change: MagicMock):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    new_value = False
    previous_value = "previous_value"
    # Act
    response = status_id_change(
        changes_to_dos=changes_to_dos,
        new_value=new_value,
        previous_value=previous_value,
    )
    # Assert
    assert response == changes_to_dos
    assert changes_to_dos.demographic_changes == {"statusid": DOS_CLOSED_STATUS_ID}
    mock_service_histories_change.assert_called_once_with(
        data=DOS_SERVICE_HISTORY_CLOSED_STATUS,
        previous_value=previous_value,
        change_key=DOS_STATUS_CHANGE_KEY,
    )
    changes_to_dos.service_histories.add_change.assert_called_once_with(
        dos_change_key=DOS_STATUS_CHANGE_KEY,
        change=mock_service_histories_change.return_value,
    )
