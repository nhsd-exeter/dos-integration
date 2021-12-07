from os import environ
from random import choices
from unittest.mock import MagicMock, patch

from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext

from ..event_processor import (
    EventProcessor,
    lambda_handler,
    update_changes,
    get_changes,
    update_changes_with_address
)
from ..nhs import NHSEntity
from .conftest import dummy_dos_service
from ..change_request import (
    ADDRESS_CHANGE_KEY,
    PHONE_CHANGE_KEY,
    POSTCODE_CHANGE_KEY,
    PUBLICNAME_CHANGE_KEY,
    WEBSITE_CHANGE_KEY,
    ChangeRequest,
)

FILE_PATH = "application.event_processor.event_processor"


def test__init__():
    # Arrange
    test_data = {}
    for i in range(10):
        random_str = "".join(choices("ABCDEFGHIJKLM", k=8))
        test_data[random_str] = random_str
    test_data["OpeningTimes"] = [{
      "Weekday": "Friday",
      "Times": "08:45-17:00",
      "OffsetOpeningTime": 525,
      "OffsetClosingTime": 1020,
      "OpeningTimeType": "General",
      "AdditionalOpeningDate": "",
      "IsOpen": True
    },
    {
      "Weekday": "Friday",
      "Times": "08:45-17:00",
      "OffsetOpeningTime": 525,
      "OffsetClosingTime": 1020,
      "OpeningTimeType": "Surgery",
      "AdditionalOpeningDate": "",
      "IsOpen": True
    },
    ]
    nhs_entity = NHSEntity(test_data)
    # Act
    event_processor = EventProcessor(nhs_entity)
    # Assert
    assert event_processor.nhs_entity == nhs_entity
    assert isinstance(event_processor.matching_services, type(None))
    assert isinstance(event_processor.change_requests, type(None))
    assert event_processor.matching_services == None
    assert event_processor.change_requests == None


def test_get_change_requests_full_change_request():
    # Arrange
    service_1 = dummy_dos_service()
    service_1.id = 1
    service_1.uid = 101
    service_1.odscode = "SLC4501"
    service_1.web = "www.fakesite.com"
    service_1.publicphone = "01462622435"
    service_1.postcode = "S45 1AB"

    nhs_entity = NHSEntity({})
    nhs_entity.ODSCode = "SLC45"
    nhs_entity.Website = "www.site.com"
    nhs_entity.Phone = "01462622435"
    nhs_entity.Postcode = "S45 1AA"
    nhs_entity.OrganisationName = "Fake NHS Service"
    nhs_entity.Address1 = "Fake Street1"
    nhs_entity.Address2 = "Fake Street2"
    nhs_entity.Address3 = "Fake Street3"
    nhs_entity.City = "Fake City"
    nhs_entity.County = "Fake County"
    nhs_entity.OpeningTimes = []

    event_processor = EventProcessor(nhs_entity)
    event_processor.matching_services = [service_1]
    # Act
    change_requests = event_processor.get_change_requests()
    # Assert

    assert (len(change_requests) == 1, 
            f"Should have 1 change request but more found: "
            f"{len(change_requests)} change requests")

    cr = change_requests[0]
    for field in ["system", "service_id", "changes"]:
        assert hasattr(cr, field), f"Attribute {field} not found in change request"

    assert (cr.system == "DoS Integration", 
            f"System should be DoS Integration but is {cr.system}")

    assert cr.changes == {
        WEBSITE_CHANGE_KEY: nhs_entity.Website,
        POSTCODE_CHANGE_KEY: nhs_entity.Postcode,
        PUBLICNAME_CHANGE_KEY: nhs_entity.OrganisationName,
        ADDRESS_CHANGE_KEY: [
            nhs_entity.Address1,
            nhs_entity.Address2,
            nhs_entity.Address3,
            nhs_entity.City,
            nhs_entity.County,
        ],
    }, "Change Request Changes not as expected"


@patch(f"{FILE_PATH}.get_matching_dos_services")
def test_get_matching_services(mock_get_matching_dos_services, change_event):
    # Arrange
    nhs_entity = NHSEntity(change_event)
    service = dummy_dos_service()
    service.typeid = 13
    service.statusid = 1
    mock_get_matching_dos_services.return_value = [service]
    event_processor = EventProcessor(nhs_entity)
    # Act
    matching_services = event_processor.get_matching_services()
    # Assert
    assert matching_services == [service]


@patch(f"{FILE_PATH}.invoke_lambda_function")
def test_send_changes(mock_invoke_lambda_function):
    # Arrange
    function_name = "test"
    environ["EVENT_SENDER_LAMBDA_NAME"] = function_name

    change_request = ChangeRequest(service_id=49016)
    change_request.reference = "1"#
    change_request.system = "Profile Updater (test)"
    change_request.message = "Test message 1531816592293|@./"
    change_request.changes = {
            PHONE_CHANGE_KEY: "0118 999 88199 9119 725 3",
            WEBSITE_CHANGE_KEY: "https://www.google.pl",
    }

    nhs_entity = NHSEntity({})
    nhs_entity.ODSCode = "SLC45"
    nhs_entity.Website = "www.site.com"
    nhs_entity.Phone = "01462622435"
    nhs_entity.Postcode = "S45 1AA"
    nhs_entity.OrganisationName = "Fake NHS Service"
    nhs_entity.Address1 = "Fake Street1"
    nhs_entity.Address2 = "Fake Street2"
    nhs_entity.Address3 = "Fake Street3"
    nhs_entity.City = "Fake City"
    nhs_entity.County = "Fake County"
    nhs_entity.OpeningTimes = []

    event_processor = EventProcessor(nhs_entity)
    event_processor.change_requests = [change_request]
    # Act
    event_processor.send_changes()
    # Assert
    mock_invoke_lambda_function.assert_called_once_with(
        function_name, 
        change_request.create_payload()
    )
    # Clean up
    del environ["EVENT_SENDER_LAMBDA_NAME"]


@patch(f"{FILE_PATH}.EventProcessor")
@patch(f"{FILE_PATH}.NHSEntity")
def test_lambda_handler_missing_environment_variable(mock_nhs_entity, mock_event_processor, change_event):
    # Arrange
    expected_env_vars = ("DB_PORT", "DB_NAME", "DB_USER_NAME", "EVENT_SENDER_LAMBDA_NAME")
    context = LambdaContext()
    context._function_name = "test"
    context._aws_request_id = "test"
    mock_entity = MagicMock()
    mock_nhs_entity.return_value = mock_entity
    for env in expected_env_vars:
        environ[env] = "test"
    # Act
    response = lambda_handler(change_event, context)
    # Assert
    assert response is None, f"Response should be None but is {response}"
    mock_nhs_entity.assert_called_once_with(change_event)
    mock_event_processor.assert_called_once_with(mock_entity)
    # Clean up
    for env in expected_env_vars:
        del environ[env]


@patch(f"{FILE_PATH}.EventProcessor")
@patch(f"{FILE_PATH}.NHSEntity")
def test_lambda_handler_mock_mode_false(mock_nhs_entity, mock_event_processor, change_event):
    # Arrange
    expected_env_vars = ("DB_SERVER", "DB_PORT", "DB_NAME", "DB_USER_NAME", "EVENT_SENDER_LAMBDA_NAME")
    context = LambdaContext()
    context._function_name = "test"
    context._aws_request_id = "test"
    mock_entity = MagicMock()
    mock_nhs_entity.return_value = mock_entity
    for env in expected_env_vars:
        environ[env] = "test"
    # Act
    response = lambda_handler(change_event, context)
    # Assert
    assert response is None, f"Response should be None but is {response}"
    mock_nhs_entity.assert_called_once_with(change_event)
    mock_event_processor.assert_called_once_with(mock_entity)
    # Clean up
    for env in expected_env_vars:
        del environ[env]


@patch(f"{FILE_PATH}.is_mock_mode")
@patch(f"{FILE_PATH}.EventProcessor")
@patch(f"{FILE_PATH}.NHSEntity")
def test_lambda_handler_mock_mode_true(mock_nhs_entity, mock_event_processor, mock_is_mock_mode, change_event):
    # Arrange
    expected_env_vars = ("DB_SERVER", "DB_PORT", "DB_NAME", "DB_USER_NAME", "EVENT_SENDER_LAMBDA_NAME")
    context = LambdaContext()
    context._function_name = "test"
    context._aws_request_id = "test"
    mock_entity = MagicMock()
    mock_nhs_entity.return_value = mock_entity
    for env in expected_env_vars:
        environ[env] = "test"
    mock_is_mock_mode.return_value = True
    # Act
    response = lambda_handler(change_event, context)
    # Assert
    assert response is None, f"Response should be None but is {response}"
    mock_nhs_entity.assert_called_once_with(change_event)
    mock_event_processor.assert_called_once_with(mock_entity)
    # Clean up
    for env in expected_env_vars:
        del environ[env]


def test_get_changes_same_data():
    # Act
    dos_service = dummy_dos_service()
    nhs_kwargs = {
        "Website": dos_service.web,
        "Postcode": dos_service.postcode,
        "Phone": dos_service.publicphone,
        "OrganisationName": dos_service.publicname,
        "Address1": dos_service.address,
        "Address2": "",
        "Address3": "",
        "City": "",
        "County": "",
        "OpeningTimes": []
    }
    nhs_entity = NHSEntity(nhs_kwargs)
    # Act
    response = get_changes(dos_service,nhs_entity)
    # Assert
    assert {} == response, f"Should return empty dict, actually: {response}"


def test_get_changes_different_changes():
    # Arrange
    dos_service = dummy_dos_service()
    website = "changed-website.com"
    postcode = "TA1 TA1"
    phone = "0123456789"
    organisation_name = "changed-organisation-name"
    address1 = "changed-address1"
    address2 = "changed-address2"
    address3 = "changed-address3"
    city = "changed-city"
    county = "changed-county"
    nhs_kwargs = {
        "Website": website,
        "Postcode": postcode,
        "Phone": phone,
        "OrganisationName": organisation_name,
        "Address1": address1,
        "Address2": address2,
        "Address3": address3,
        "City": city,
        "County": county,
        "OpeningTimes": []
    }
    nhs_entity = NHSEntity(nhs_kwargs)
    expected_changes = {
        ADDRESS_CHANGE_KEY: [address1, address2, address3, city, county],
        PUBLICNAME_CHANGE_KEY: organisation_name,
        WEBSITE_CHANGE_KEY: website,
        POSTCODE_CHANGE_KEY: postcode,
        PHONE_CHANGE_KEY: phone,
    }
    # Act
    response = get_changes(dos_service,nhs_entity)
    # Assert
    assert expected_changes == response, f"Should return {expected_changes} dict, actually: {response}"


def test_update_changes_publicphone_to_change_request_if_not_equal_is_equal():
    # Arrange
    changes = {}
    # Act
    update_changes(changes, PHONE_CHANGE_KEY, "000000000", "000000000")
    update_changes(changes, PUBLICNAME_CHANGE_KEY, "boots", "boots")
    update_changes(changes, WEBSITE_CHANGE_KEY, "www.wow.co.uk", "www.wow.co.uk")
    # Assert
    assert changes == {}, f"Should return empty dict, actually: {changes}"


def test_update_changes_publicphone_to_change_request_if_not_equal_not_equal():
    # Arrange
    changes = {}
    nhs_uk_phone = "000000000"
    dos_public_phone = "123456789"
    expected_changes = {"publicphone": nhs_uk_phone}
    # Act
    update_changes(changes, "publicphone", dos_public_phone, nhs_uk_phone)
    # Assert
    assert (changes == expected_changes, 
            f"Should return {expected_changes} dict, actually: {changes}")


def test_update_changes_address_to_change_request_if_not_equal_is_equal():
    # Arrange
    changes = {}
    test_data = {}
    test_data["OpeningTimes"] = []
    nhs_uk_entity = NHSEntity(test_data)
    nhs_uk_entity.Address1 = "address1"
    nhs_uk_entity.Address2 = "address2"
    nhs_uk_entity.Address3 = "address3"
    nhs_uk_entity.City = "city"
    nhs_uk_entity.County = "county"
    nhs_uk_entity.OpeningTimes= []
    dos_address = (
        f"{nhs_uk_entity.Address1}${nhs_uk_entity.Address2}$"
        f"{nhs_uk_entity.Address3}${nhs_uk_entity.City}${nhs_uk_entity.County}"
    )
    # Act
    actual_changes = update_changes_with_address(changes, "address", dos_address, nhs_uk_entity)
    # Assert
    assert changes == actual_changes, f"Should return {changes} dict, actually: {actual_changes}"


def test_update_changes_address_to_change_request_if_not_equal_not_equal():
    # Arrange
    changes = {}
    test_data = {}
    test_data["OpeningTimes"] = []
    nhs_uk_entity = NHSEntity(test_data)
    nhs_uk_entity.Address1 = "address1"
    nhs_uk_entity.Address2 = "address2"
    nhs_uk_entity.Address3 = "address3"
    nhs_uk_entity.City = "city"
    nhs_uk_entity.County = "county"
    dos_address = "Test RD$Testown$Testshire"
    expected_changes = {
        ADDRESS_CHANGE_KEY: [
            nhs_uk_entity.Address1,
            nhs_uk_entity.Address2,
            nhs_uk_entity.Address3,
            nhs_uk_entity.City,
            nhs_uk_entity.County,
        ]
    }
    # Act
    actual_changes = update_changes_with_address(changes, "address", dos_address, nhs_uk_entity)
    # Assert
    assert expected_changes == actual_changes, f"Should return {changes} dict, actually: {actual_changes}"

