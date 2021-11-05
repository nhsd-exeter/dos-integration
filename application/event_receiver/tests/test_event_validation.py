from ..event_validation import validate_event, check_organisation_type
from .change_events import STANDARD_EVENT


def test_validate_event():
    # Arrange
    # Act
    response = validate_event(STANDARD_EVENT)
    # Assert
    assert response is True


def test_validate_event_missing_key():
    # Arrange
    event = STANDARD_EVENT.copy()
    del event["ODSCode"]
    # Act
    response = validate_event(event)
    # Assert
    assert response is False


def test_check_organisation_type():
    # Arrange
    event = STANDARD_EVENT.copy()
    odscode = event.pop("ODSCode")
    # Act
    response = check_organisation_type(odscode)
    # Assert
    assert response is False
