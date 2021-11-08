from unittest.mock import patch

import pytest
from pytest import fixture, raises
from testfixtures import LogCapture

from ..change_event_validation import ValidationException, check_ods_code_length, check_organisation_type, valid_event

FILE_PATH = "application.event_receiver.change_event_validation"


def test_valid_event(change_event):
    # Act
    response = valid_event(change_event["body"])
    # Assert
    assert response is True


@patch(f"{FILE_PATH}.check_organisation_type")
@patch(f"{FILE_PATH}.check_ods_code_length")
def test_validate_event_missing_key(
    mock_check_ods_code_length, mock_check_organisation_type, change_event, log_capture
):
    # Arrange
    del change_event["body"]["ODSCode"]
    # Act
    response = valid_event(change_event["body"])
    # Assert
    mock_check_ods_code_length.assert_not_called()
    mock_check_organisation_type.assert_not_called()
    assert "Input schema validation error|" in log_capture[0][2]
    assert response is False


@pytest.mark.parametrize("organisation_type", ["Pharmacy"])
def test_check_organisation_type(organisation_type):
    # Act & Assert
    check_organisation_type(organisation_type)


@pytest.mark.parametrize("organisation_type", ["Not Expected Type", "Dentist", "Pharmacy Out of hours"])
def test_check_organisation_type_wrong_organisation_type(organisation_type):
    # Act & Assert
    with raises(ValidationException):
        check_organisation_type(organisation_type)


@pytest.mark.parametrize("odscode", ["FXXX1", "AAAAA", "00000"])
def test_check_ods_code_length(odscode):
    # Act & Assert
    check_ods_code_length(odscode)


@pytest.mark.parametrize("odscode", ["FXXX11", "AAAA"])
def test_check_ods_code_length_incorrect_length(odscode):
    # Act & Assert
    with raises(ValidationException):
        check_ods_code_length(odscode)


@fixture()
def log_capture():
    with LogCapture(names="lambda") as capture:
        yield capture


@fixture
def change_event():
    change_event = PHARMACY_STANDARD_EVENT.copy()
    yield change_event


PHARMACY_STANDARD_EVENT = {
    "body": {
        "SearchKey": "ANEI1245",
        "ODSCode": "FX111",
        "OrganisationName": "My Test Pharmacy",
        "OrganisationTypeId": "PH1",
        "OrganisationType": "Pharmacy",
        "OrganisationStatus": "Visible",
        "SummaryText": "",
        "URL": "https://my-pharmacy.com/",
        "Address1": "85 Peachfield Road",
        "Address2": None,
        "Address3": None,
        "City": "CHAPEL ROW",
        "County": "South Godshire",
        "Latitude": 53.38030624389648,
        "Longitude": -1.4826949834823608,
        "Postcode": "RG7 1DB",
        "Phone": "123456789",
        "Email": "health.my-pharmacy@nhs.net",
        "Website": "https://my-pharmacy.com/health-service",
        "OrganisationSubType": None,
        "OrganisationAliases": [],
    }
}
