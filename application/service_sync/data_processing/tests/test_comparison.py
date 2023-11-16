from unittest.mock import MagicMock, patch

import pytest
from aws_lambda_powertools.logging import Logger

from application.common.commissioned_service_type import CommissionedServiceType
from application.common.dos_location import DoSLocation
from application.common.opening_times import WEEKDAYS
from application.service_sync.data_processing.changes_to_dos import ChangesToDoS
from application.service_sync.data_processing.comparison import (
    compare_blood_pressure,
    compare_commissioned_service,
    compare_contraception,
    compare_location,
    compare_palliative_care,
    compare_public_phone,
    compare_specified_opening_times,
    compare_standard_opening_times,
    compare_website,
)

FILE_PATH = "application.service_sync.data_processing.comparison"


@patch(f"{FILE_PATH}.is_val_none_or_empty")
@patch(f"{FILE_PATH}.format_website")
def test_compare_website_remove_website(
    mock_format_website: MagicMock,
    mock_is_val_none_or_empty: MagicMock,
) -> None:
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    mock_is_val_none_or_empty.side_effect = [True, False]
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    # Act
    response = compare_website(changes=changes_to_dos)
    # Assert
    assert True is response
    mock_format_website.assert_not_called()


@patch(f"{FILE_PATH}.validate_website")
@patch(f"{FILE_PATH}.format_website")
@patch(f"{FILE_PATH}.is_val_none_or_empty")
@patch(f"{FILE_PATH}.format_website")
def test_compare_website_add_website(
    mock_format_website: MagicMock,
    mock_is_val_none_or_empty: MagicMock,
    format_website: MagicMock,
    mock_validate_website: MagicMock,
) -> None:
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    format_website.return_value = nhs_website = "www.example2.com"
    service_histories = MagicMock()
    mock_is_val_none_or_empty.side_effect = [False, False]
    mock_validate_website.return_value = True
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    # Act
    response = compare_website(changes=changes_to_dos)
    # Assert
    assert True is response
    assert dos_service.web == changes_to_dos.current_website
    assert nhs_website == changes_to_dos.new_website
    mock_format_website.assert_not_called()
    mock_validate_website.assert_called_once_with(nhs_entity, nhs_website, dos_service)


@patch(f"{FILE_PATH}.validate_website")
@patch(f"{FILE_PATH}.is_val_none_or_empty")
@patch(f"{FILE_PATH}.format_website")
def test_compare_website_no_change(
    mock_format_website: MagicMock,
    mock_is_val_none_or_empty: MagicMock,
    mock_validate_website: MagicMock,
) -> None:
    # Arrange
    dos_service = MagicMock()
    dos_service.web = "www.example2.com"
    nhs_entity = MagicMock()
    nhs_entity.website = dos_service.web
    mock_format_website.return_value = dos_service.web
    service_histories = MagicMock()
    mock_is_val_none_or_empty.side_effect = [True, True]
    mock_validate_website.return_value = True
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    # Act
    response = compare_website(changes=changes_to_dos)
    # Assert
    assert False is response
    mock_format_website.assert_called_once_with(nhs_entity.website)
    mock_validate_website.assert_not_called()


@patch(f"{FILE_PATH}.get_valid_dos_location")
def test_compare_location(mock_get_valid_dos_location: MagicMock) -> None:
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    dummy_dos_location = DoSLocation(
        id=0,
        postcode="DUMMY",
        easting=0,
        northing=0,
        postaltown="STUB",
        latitude=0,
        longitude=0,
    )
    mock_get_valid_dos_location.return_value = dummy_dos_location
    # Act
    address_response, postcode_response, dos_location = compare_location(changes_to_dos)
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
def test_compare_location_postcode_invalid(
    mock_get_valid_dos_location: MagicMock,
    mock_log_invalid_nhsuk_postcode: MagicMock,
) -> None:
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    mock_get_valid_dos_location.return_value = None
    # Act
    address_response, postcode_response, dos_location = compare_location(changes_to_dos)
    # Assert
    assert False is address_response
    assert False is postcode_response
    assert None is changes_to_dos.new_address
    assert None is changes_to_dos.new_postcode
    assert None is changes_to_dos.current_address
    assert None is changes_to_dos.current_postcode
    mock_get_valid_dos_location.assert_called_once()
    mock_log_invalid_nhsuk_postcode.assert_called_once()
    assert mock_get_valid_dos_location.return_value == dos_location


@patch(f"{FILE_PATH}.get_valid_dos_location")
def test_has_location_changed_no_change(mock_get_valid_dos_location: MagicMock) -> None:
    # Arrange
    dos_service = MagicMock()
    dos_service.address = "1 Dummy Stub"
    dos_service.normal_postcode.return_value = "DUMMY"
    nhs_entity = MagicMock()
    nhs_entity.address_lines = {dos_service.address}
    nhs_entity.normal_postcode.return_value = "DUMMY"
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)

    # Act
    address_response, postcode_response, dos_location = compare_location(changes_to_dos)
    # Assert
    assert False is address_response
    assert False is postcode_response
    assert None is changes_to_dos.new_address
    assert None is changes_to_dos.new_postcode
    assert None is changes_to_dos.current_address
    assert None is changes_to_dos.current_postcode
    mock_get_valid_dos_location.assert_not_called()


def test_compare_public_phone() -> None:
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    dos_service.publicphone = "0123456789"
    nhs_entity.publicphone = "012345678"
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    # Act
    response = compare_public_phone(changes=changes_to_dos)
    # Assert
    assert True is response


def test_compare_public_phone_no_change() -> None:
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    dos_service.publicphone = "0123456789"
    nhs_entity.phone = "0123456789"
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    # Act
    response = compare_public_phone(changes=changes_to_dos)
    # Assert
    assert False is response


@pytest.mark.parametrize("weekday", WEEKDAYS)
def test_compare_standard_opening_times(weekday: str):
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    dos_service.standard_opening_times.same_openings.return_value = False
    # Act
    compare_standard_opening_times(changes_to_dos, weekday)
    # Assert
    assert hasattr(changes_to_dos, f"current_{weekday}_opening_times")
    assert hasattr(changes_to_dos, f"new_{weekday}_opening_times")


@pytest.mark.parametrize("weekday", WEEKDAYS)
def test_compare_standard_opening_times_no_changes(weekday: str) -> None:
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    dos_service.standard_opening_times.same_openings.return_value = True
    # Act
    compare_standard_opening_times(changes_to_dos, weekday)
    # Assert
    assert False is hasattr(changes_to_dos, f"current_{weekday}_opening_times")
    assert False is hasattr(changes_to_dos, f"new_{weekday}_opening_times")


@patch(f"{FILE_PATH}.SpecifiedOpeningTime")
def test_compare_specified_opening_times_changed(mock_specified_opening_time: MagicMock) -> None:
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    mock_specified_opening_time.equal_lists.return_value = False
    mock_specified_opening_time.remove_past_dates.return_value = ["2020-01-01"]
    # Act
    response = compare_specified_opening_times(changes=changes_to_dos)
    # Assert
    assert True is response
    assert None is not changes_to_dos.new_specified_opening_times
    assert None is not changes_to_dos.current_specified_opening_times


@patch(f"{FILE_PATH}.SpecifiedOpeningTime")
def test_compare_specified_opening_times_changed_no_change(mock_specified_opening_time: MagicMock) -> None:
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    mock_specified_opening_time.equal_lists.return_value = True
    # Act
    response = compare_specified_opening_times(changes=changes_to_dos)
    # Assert
    assert False is response
    assert None is changes_to_dos.new_specified_opening_times
    assert None is changes_to_dos.current_specified_opening_times


def test_compare_palliative_care() -> None:
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    dos_service.palliative_care = True
    nhs_entity.palliative_care = False
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    # Act
    response = compare_palliative_care(changes=changes_to_dos)
    # Assert
    assert True is response


def test_compare_palliative_care_no_change() -> None:
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    dos_service.palliative_care = False
    nhs_entity.palliative_care = False
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)
    # Act
    response = compare_palliative_care(changes=changes_to_dos)
    # Assert
    assert False is response


def test_compare_blood_pressure_no_changes() -> None:
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    dos_service.blood_pressure = True
    nhs_entity.blood_pressure = True
    changes_to_dos = ChangesToDoS(
        dos_service=dos_service,
        nhs_entity=nhs_entity,
        service_histories=service_histories,
    )
    # Act
    response = compare_blood_pressure(changes=changes_to_dos)
    # Assert
    assert False is response


def test_compare_blood_pressure() -> None:
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    dos_service.blood_pressure = True
    nhs_entity.blood_pressure = False
    changes_to_dos = ChangesToDoS(
        dos_service=dos_service,
        nhs_entity=nhs_entity,
        service_histories=service_histories,
    )

    # Act
    response = compare_blood_pressure(changes=changes_to_dos)
    # Assert
    assert True is response


def test_compare_contraception_pressure_no_changes() -> None:
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    dos_service.contraception = True
    nhs_entity.contraception = True
    changes_to_dos = ChangesToDoS(
        dos_service=dos_service,
        nhs_entity=nhs_entity,
        service_histories=service_histories,
    )
    # Act
    response = compare_contraception(changes=changes_to_dos)
    # Assert
    assert False is response


def test_compare_contraception() -> None:
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    dos_service.contraception = True
    nhs_entity.contraception = False
    changes_to_dos = ChangesToDoS(
        dos_service=dos_service,
        nhs_entity=nhs_entity,
        service_histories=service_histories,
    )
    # Act
    response = compare_contraception(changes=changes_to_dos)
    # Assert
    assert True is response


@patch.object(Logger, "info")
def test_compare_commissioned_service(mock_logger: MagicMock) -> None:
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    stub_service_type = CommissionedServiceType(
        TYPE_NAME="Stub Type",
        NHS_UK_SERVICE_CODE="SN000",
        DOS_TYPE_ID=999,
        DOS_SYMPTOM_GROUP=360,
        DOS_SYMPTOM_DISCRIMINATOR=9999,
        DOS_SG_SD_ID="360=9999",
    )
    dos_service.stub_type = True
    nhs_entity.stub_type = False
    changes_to_dos = ChangesToDoS(
        dos_service=dos_service,
        nhs_entity=nhs_entity,
        service_histories=service_histories,
    )
    # Act
    response = compare_commissioned_service(changes=changes_to_dos, service_type=stub_service_type)
    # Assert
    mock_logger.assert_called_once_with(
        f"{stub_service_type.TYPE_NAME} is not equal, DoS='{dos_service.stub_type}' != NHS UK='{nhs_entity.stub_type}'",
        extra={
            f"dos_{stub_service_type.TYPE_NAME}": dos_service.stub_type,
            f"nhsuk_{stub_service_type.TYPE_NAME}": nhs_entity.stub_type,
        },
    )
    assert True is response


@patch.object(Logger, "info")
def test_compare_commissioned_service_no_change(mock_logger: MagicMock) -> None:
    # Arrange
    dos_service = MagicMock()
    nhs_entity = MagicMock()
    service_histories = MagicMock()
    stub_service_type = CommissionedServiceType(
        TYPE_NAME="Stub Type",
        NHS_UK_SERVICE_CODE="SN000",
        DOS_TYPE_ID=999,
        DOS_SYMPTOM_GROUP=360,
        DOS_SYMPTOM_DISCRIMINATOR=9999,
        DOS_SG_SD_ID="360=9999",
    )
    dos_service.stub_type = True
    nhs_entity.stub_type = True
    changes_to_dos = ChangesToDoS(
        dos_service=dos_service,
        nhs_entity=nhs_entity,
        service_histories=service_histories,
    )
    # Act
    response = compare_commissioned_service(changes=changes_to_dos, service_type=stub_service_type)
    # Assert
    mock_logger.assert_called_once_with(
        f"{stub_service_type.TYPE_NAME} is equal, DoS='{dos_service.stub_type}' == NHS UK='{nhs_entity.stub_type}'"
    )
    assert False is response
