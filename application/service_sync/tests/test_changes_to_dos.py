from unittest.mock import MagicMock, patch

from pytest import mark

from application.common.opening_times import WEEKDAYS
from application.service_sync.changes_to_dos import ChangesToDoS, compare_nhs_uk_and_dos_data

FILE_PATH = "application.service_sync.changes_to_dos"


def test_changes_to_dos():
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    # Act
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    # Assert
    assert dos_service == changes_to_dos.dos_service
    assert nhs_entity == changes_to_dos.nhs_entity
    assert service_histories == changes_to_dos.service_histories
    assert {} == changes_to_dos.demographic_changes
    assert {} == changes_to_dos.standard_opening_times_changes
    assert False is changes_to_dos.specified_opening_times_changes
    assert None is changes_to_dos.new_address
    assert None is changes_to_dos.new_postcode
    assert None is changes_to_dos.new_public_phone
    assert None is changes_to_dos.new_specified_opening_times
    assert None is changes_to_dos.new_website
    assert None is changes_to_dos.current_address
    assert None is changes_to_dos.current_postcode
    assert None is changes_to_dos.current_public_phone
    assert None is changes_to_dos.current_specified_opening_times
    assert None is changes_to_dos.current_website


@mark.parametrize("weekday", WEEKDAYS)
def test_changes_to_dos_check_for_standard_opening_times_day_changes(weekday: str):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    dos_service.standard_opening_times.same_openings.return_value = False
    # Act
    changes_to_dos.check_for_standard_opening_times_day_changes(weekday)
    # Assert
    assert hasattr(changes_to_dos, f"current_{weekday}_opening_times")
    assert hasattr(changes_to_dos, f"new_{weekday}_opening_times")


@mark.parametrize("weekday", WEEKDAYS)
def test_changes_to_dos_check_for_standard_opening_times_day_changes_no_changes(weekday: str):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    dos_service.standard_opening_times.same_openings.return_value = True
    # Act
    changes_to_dos.check_for_standard_opening_times_day_changes(weekday)
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
    response = changes_to_dos.check_for_specified_opening_times_changes()
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
    response = changes_to_dos.check_for_specified_opening_times_changes()
    # Assert
    assert False is response
    assert None is changes_to_dos.new_specified_opening_times
    assert None is changes_to_dos.current_specified_opening_times


@patch(f"{FILE_PATH}.get_valid_dos_postcode")
def test_changes_to_dos_check_for_address_and_postcode_for_changes(mock_get_valid_dos_postcode):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    # Act
    address_response, postcode_response = changes_to_dos.check_for_address_and_postcode_for_changes()
    # Assert
    assert True is address_response
    assert True is postcode_response
    assert None is not changes_to_dos.new_address
    assert None is not changes_to_dos.new_postcode
    assert None is not changes_to_dos.current_address
    assert None is not changes_to_dos.current_postcode
    mock_get_valid_dos_postcode.assert_called_once()


@patch(f"{FILE_PATH}.log_invalid_nhsuk_postcode")
@patch(f"{FILE_PATH}.get_valid_dos_postcode")
def test_changes_to_dos_check_for_address_and_postcode_for_changes_postcode_invalid(
    mock_get_valid_dos_postcode: MagicMock, mock_log_invalid_nhsuk_postcode: MagicMock
):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    mock_get_valid_dos_postcode.return_value = None
    # Act
    address_response, postcode_response = changes_to_dos.check_for_address_and_postcode_for_changes()
    # Assert
    assert False is address_response
    assert False is postcode_response
    assert None is changes_to_dos.new_address
    assert None is changes_to_dos.new_postcode
    assert None is changes_to_dos.current_address
    assert None is changes_to_dos.current_postcode
    mock_get_valid_dos_postcode.assert_called_once()


@patch(f"{FILE_PATH}.is_val_none_or_empty")
@patch(f"{FILE_PATH}.format_website")
def test_changes_to_dos_check_website_for_change_remove_website(
    mock_format_website: MagicMock, mock_is_val_none_or_empty: MagicMock
):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    mock_is_val_none_or_empty.side_effect = [True, False]
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    # Act
    response = changes_to_dos.check_website_for_change()
    # Assert
    assert True is response
    mock_format_website.assert_not_called()


@patch(f"{FILE_PATH}.ChangesToDoS.compare_and_validate_website")
@patch(f"{FILE_PATH}.format_website")
@patch(f"{FILE_PATH}.is_val_none_or_empty")
@patch(f"{FILE_PATH}.format_website")
def test_changes_to_dos_check_website_for_change_add_website(
    mock_format_website: MagicMock,
    mock_is_val_none_or_empty: MagicMock,
    format_website: MagicMock,
    mock_compare_and_validate_website: MagicMock,
):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    format_website.return_value = nhs_website = "www.example2.com"
    service_histories = MagicMock()
    mock_is_val_none_or_empty.side_effect = [False, False]
    mock_compare_and_validate_website.return_value = True
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    # Act
    response = changes_to_dos.check_website_for_change()
    # Assert
    assert True is response
    assert dos_service.web == changes_to_dos.current_website
    assert nhs_website == changes_to_dos.new_website
    mock_format_website.assert_not_called()
    mock_compare_and_validate_website.assert_called_once_with(dos_service, nhs_entity, nhs_website)


@patch(f"{FILE_PATH}.validate_website")
def test_changes_to_dos_compare_and_validate_website_same_value(mock_validate_website: MagicMock):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    nhs_website = "www.example2.com"
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    mock_validate_website.return_value = True
    # Act
    response = changes_to_dos.compare_and_validate_website(dos_service, nhs_entity, nhs_website)
    # Assert
    assert True is response
    mock_validate_website.assert_called_once_with(nhs_entity, nhs_website)


@patch(f"{FILE_PATH}.validate_website")
def test_changes_to_dos_compare_and_validate_website_different_value(mock_validate_website: MagicMock):
    # Arrange
    dos_service = MagicMock()
    dos_service.web = "www.example.com"
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    nhs_website = "www.example.com"
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    mock_validate_website.return_value = False
    # Act
    response = changes_to_dos.compare_and_validate_website(dos_service, nhs_entity, nhs_website)
    # Assert
    assert False is response
    mock_validate_website.assert_not_called()


def test_changes_to_dos_check_public_phone_for_change():
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    dos_service.publicphone = "0123456789"
    nhs_entity.publicphone = "012345678"
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    # Act
    response = changes_to_dos.check_public_phone_for_change()
    # Assert
    assert True is response


def test_changes_to_dos_check_public_phone_for_change_no_change():
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    dos_service.publicphone = "0123456789"
    nhs_entity.publicphone = "0123456789"
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    # Act
    response = changes_to_dos.check_public_phone_for_change()
    # Assert
    assert True is response


@patch(f"{FILE_PATH}.validate_opening_times")
@patch(f"{FILE_PATH}.ChangesToDoS")
def test_compare_nhs_uk_and_dos_data(mock_changes_to_dos: MagicMock, mock_validate_opening_times: MagicMock):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    mock_changes_to_dos.return_value.check_for_address_and_postcode_for_changes.return_value = (True, True)
    mock_validate_opening_times.return_value = True
    # Act
    compare_nhs_uk_and_dos_data(dos_service, nhs_entity, service_histories)
    # Assert
    mock_changes_to_dos.return_value.check_website_for_change.assert_called_once_with()
    mock_changes_to_dos.return_value.check_public_phone_for_change.assert_called_once_with()
    mock_changes_to_dos.return_value.check_for_address_and_postcode_for_changes.assert_called_once_with()
    assert 7 == mock_changes_to_dos.return_value.check_for_standard_opening_times_day_changes.call_count
    mock_changes_to_dos.return_value.check_for_specified_opening_times_changes.assert_called_once_with()
    mock_validate_opening_times.assert_called_once_with(
        dos_service=mock_changes_to_dos.return_value.dos_service, nhs_entity=mock_changes_to_dos.return_value.nhs_entity
    )


@patch(f"{FILE_PATH}.validate_opening_times")
@patch(f"{FILE_PATH}.ChangesToDoS")
def test_compare_nhs_uk_and_dos_data_invalid_opening_times(
    mock_changes_to_dos: MagicMock, mock_validate_opening_times: MagicMock
):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    mock_changes_to_dos.return_value.check_for_address_and_postcode_for_changes.return_value = (True, True)
    mock_validate_opening_times.return_value = False
    # Act
    compare_nhs_uk_and_dos_data(dos_service, nhs_entity, service_histories)
    # Assert
    mock_changes_to_dos.return_value.check_website_for_change.assert_called_once_with()
    mock_changes_to_dos.return_value.check_public_phone_for_change.assert_called_once_with()
    mock_changes_to_dos.return_value.check_for_address_and_postcode_for_changes.assert_called_once_with()
    assert 0 == mock_changes_to_dos.return_value.check_for_standard_opening_times_day_changes.call_count
    mock_changes_to_dos.return_value.check_for_specified_opening_times_changes.assert_not_called()
    mock_validate_opening_times.assert_called_once_with(
        dos_service=mock_changes_to_dos.return_value.dos_service, nhs_entity=mock_changes_to_dos.return_value.nhs_entity
    )
