from unittest.mock import MagicMock

from application.service_sync.data_processing.changes_to_dos import ChangesToDoS

FILE_PATH = "application.service_sync.data_processing.changes_to_dos"


def test_changes_to_dos() -> None:
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
    assert changes_to_dos.demographic_changes == {}
    assert changes_to_dos.standard_opening_times_changes == {}
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
