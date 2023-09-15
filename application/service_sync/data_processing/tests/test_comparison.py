from unittest.mock import MagicMock, patch

import pytest

from application.common.constants import (
    DOS_BLOOD_PRESSURE_SYMPTOM_DISCRIMINATOR,
    DOS_BLOOD_PRESSURE_SYMPTOM_GROUP,
    DOS_CONTRACEPTION_SYMPTOM_DISCRIMINATOR,
    DOS_CONTRACEPTION_SYMPTOM_GROUP,
)
from application.common.dos_location import DoSLocation
from application.common.opening_times import WEEKDAYS
from application.service_sync.data_processing.changes_to_dos import ChangesToDoS
from application.service_sync.data_processing.comparison import (
    compare_blood_pressure,
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
):
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
    mock_validate_website,
):
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
def test_compare_location(mock_get_valid_dos_location: MagicMock):
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
):
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
def test_has_location_changed_no_change(mock_get_valid_dos_location: MagicMock):
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


def test_compare_public_phone():
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


def test_compare_public_phone_no_change():
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
def test_compare_standard_opening_times_no_changes(weekday: str):
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
def test_compare_specified_opening_times_changed(mock_specified_opening_time: MagicMock):
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
def test_compare_specified_opening_times_changed_no_change(mock_specified_opening_time: MagicMock):
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


def test_compare_palliative_care():
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


def test_compare_palliative_care_no_change():
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


@patch(f"{FILE_PATH}.validate_z_code_exists")
@patch(f"{FILE_PATH}.connect_to_dos_db")
def test_compare_blood_pressure_no_changes(
    mock_connect_to_dos_db: MagicMock,
    mock_validate_z_code_exists: MagicMock,
) -> None:
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
    mock_validate_z_code_exists.return_value = True
    # Act
    response = compare_blood_pressure(changes=changes_to_dos)
    # Assert
    assert False is response
    mock_validate_z_code_exists.assert_called_once_with(
        connection=mock_connect_to_dos_db.return_value.__enter__.return_value,
        dos_service=changes_to_dos.dos_service,
        symptom_group_id=DOS_BLOOD_PRESSURE_SYMPTOM_GROUP,
        symptom_discriminator_id=DOS_BLOOD_PRESSURE_SYMPTOM_DISCRIMINATOR,
        z_code_alias="Blood Pressure",
    )


@patch(f"{FILE_PATH}.validate_z_code_exists")
@patch(f"{FILE_PATH}.connect_to_dos_db")
def test_compare_blood_pressure_valid_z_code(
    mock_connect_to_dos_db: MagicMock,
    mock_validate_z_code_exists: MagicMock,
) -> None:
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
    mock_validate_z_code_exists.return_value = True
    # Act
    response = compare_blood_pressure(changes=changes_to_dos)
    # Assert
    assert True is response
    mock_validate_z_code_exists.assert_called_once_with(
        connection=mock_connect_to_dos_db.return_value.__enter__.return_value,
        dos_service=changes_to_dos.dos_service,
        symptom_group_id=DOS_BLOOD_PRESSURE_SYMPTOM_GROUP,
        symptom_discriminator_id=DOS_BLOOD_PRESSURE_SYMPTOM_DISCRIMINATOR,
        z_code_alias="Blood Pressure",
    )


@patch(f"{FILE_PATH}.add_metric")
@patch(f"{FILE_PATH}.validate_z_code_exists")
@patch(f"{FILE_PATH}.connect_to_dos_db")
def test_compare_blood_pressure_not_valid_z_code(
    mock_connect_to_dos_db: MagicMock,
    mock_validate_z_code_exists: MagicMock,
    mock_add_metric: MagicMock,
) -> None:
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
    mock_validate_z_code_exists.return_value = False
    # Act
    response = compare_blood_pressure(changes=changes_to_dos)
    # Assert
    assert True is response
    mock_validate_z_code_exists.assert_called_once_with(
        connection=mock_connect_to_dos_db.return_value.__enter__.return_value,
        dos_service=changes_to_dos.dos_service,
        symptom_group_id=DOS_BLOOD_PRESSURE_SYMPTOM_GROUP,
        symptom_discriminator_id=DOS_BLOOD_PRESSURE_SYMPTOM_DISCRIMINATOR,
        z_code_alias="Blood Pressure",
    )
    mock_add_metric.assert_called_once_with("DoSBloodPressureZCodeDoesNotExist")


@patch(f"{FILE_PATH}.validate_z_code_exists")
@patch(f"{FILE_PATH}.connect_to_dos_db")
def test_compare_contraception_pressure_no_changes(
    mock_connect_to_dos_db: MagicMock,
    mock_validate_z_code_exists: MagicMock,
) -> None:
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
    mock_validate_z_code_exists.return_value = True
    # Act
    response = compare_contraception(changes=changes_to_dos)
    # Assert
    assert False is response
    mock_validate_z_code_exists.assert_called_once_with(
        connection=mock_connect_to_dos_db.return_value.__enter__.return_value,
        dos_service=changes_to_dos.dos_service,
        symptom_group_id=DOS_CONTRACEPTION_SYMPTOM_GROUP,
        symptom_discriminator_id=DOS_CONTRACEPTION_SYMPTOM_DISCRIMINATOR,
        z_code_alias="Contraception",
    )


@patch(f"{FILE_PATH}.validate_z_code_exists")
@patch(f"{FILE_PATH}.connect_to_dos_db")
def test_compare_contraception_valid_z_code(
    mock_connect_to_dos_db: MagicMock,
    mock_validate_z_code_exists: MagicMock,
) -> None:
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
    mock_validate_z_code_exists.return_value = True
    # Act
    response = compare_contraception(changes=changes_to_dos)
    # Assert
    assert True is response
    mock_validate_z_code_exists.assert_called_once_with(
        connection=mock_connect_to_dos_db.return_value.__enter__.return_value,
        dos_service=changes_to_dos.dos_service,
        symptom_group_id=DOS_CONTRACEPTION_SYMPTOM_GROUP,
        symptom_discriminator_id=DOS_CONTRACEPTION_SYMPTOM_DISCRIMINATOR,
        z_code_alias="Contraception",
    )


@patch(f"{FILE_PATH}.add_metric")
@patch(f"{FILE_PATH}.validate_z_code_exists")
@patch(f"{FILE_PATH}.connect_to_dos_db")
def test_compare_contraception_not_valid_z_code(
    mock_connect_to_dos_db: MagicMock,
    mock_validate_z_code_exists: MagicMock,
    mock_add_metric: MagicMock,
) -> None:
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
    mock_validate_z_code_exists.return_value = False
    # Act
    response = compare_contraception(changes=changes_to_dos)
    # Assert
    assert True is response
    mock_validate_z_code_exists.assert_called_once_with(
        connection=mock_connect_to_dos_db.return_value.__enter__.return_value,
        dos_service=changes_to_dos.dos_service,
        symptom_group_id=DOS_CONTRACEPTION_SYMPTOM_GROUP,
        symptom_discriminator_id=DOS_CONTRACEPTION_SYMPTOM_DISCRIMINATOR,
        z_code_alias="Contraception",
    )
    mock_add_metric.assert_called_once_with("DoSContraceptionZCodeDoesNotExist")
