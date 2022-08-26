from unittest.mock import MagicMock, patch

from application.service_sync.compare_data import (
    compare_nhs_uk_and_dos_data,
    compare_website,
)
from application.common.constants import DOS_WEBSITE_CHANGE_KEY

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
        dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories
    )
    mock_compare_website.assert_called_once_with(changes_to_dos=mock_changes_to_dos.return_value)
    mock_compare_public_phone.assert_called_once_with(changes_to_dos=mock_compare_website.return_value)
    mock_compare_location_data.assert_called_once_with(changes_to_dos=mock_compare_public_phone.return_value)
    mock_compare_opening_times.assert_called_once_with(changes_to_dos=mock_compare_location_data.return_value)
    assert response == mock_compare_opening_times.return_value


@patch(f"{FILE_PATH}.set_up_for_services_table_change")
def test_compare_website(mock_set_up_for_services_table_change: MagicMock):
    # Arrange
    changes_to_dos = MagicMock()
    changes_to_dos.check_website_for_change.return_value = True
    changes_to_dos.new_website = new_website = "new_website"
    changes_to_dos.current_website = current_website = "current_website"
    # Act
    response = compare_website(changes_to_dos)
    # Assert
    assert response == mock_set_up_for_services_table_change.return_value
    changes_to_dos.check_website_for_change.assert_called_once_with()
    mock_set_up_for_services_table_change.assert_called_once_with(
        changes_to_dos=changes_to_dos,
        change_key=DOS_WEBSITE_CHANGE_KEY,
        new_value=new_website,
        previous_value=current_website,
        service_table_field_name="web",
    )


@patch(f"{FILE_PATH}.set_up_for_services_table_change")
def test_compare_website_no_change(mock_set_up_for_services_table_change: MagicMock):
    # Arrange
    changes_to_dos = MagicMock()
    changes_to_dos.check_website_for_change.return_value = False
    changes_to_dos.new_website = "new_website"
    changes_to_dos.current_website = "current_website"
    # Act
    response = compare_website(changes_to_dos)
    # Assert
    assert response == changes_to_dos
    changes_to_dos.check_website_for_change.assert_called_once_with()
    mock_set_up_for_services_table_change.assert_not_called()
