from ..change_request import (
    ADDRESS_CHANGE_KEY,
    OPENING_DATES_KEY,
    OPENING_DAYS_KEY,
    PHONE_CHANGE_KEY,
    POSTCODE_CHANGE_KEY,
    PUBLICNAME_CHANGE_KEY,
    WEBSITE_CHANGE_KEY,
)
from ..changes import get_changes, update_changes, update_changes_with_address, update_changes_with_opening_times
from ..nhs import NHSEntity
from .conftest import dummy_dos_location, dummy_dos_service
from dos import dos_location_cache

FILE_PATH = "application.event_processor.changes"


def test_get_changes_same_data():
    # Act
    dos_service = dummy_dos_service()
    nhs_entity = NHSEntity({
        "Postcode": dos_service.postcode,
        "Phone": dos_service.publicphone,
        "OrganisationName": dos_service.publicname,
        "Address1": dos_service.address,
        "Contacts": [{
            "ContactType": "Primary",
            "ContactAvailabilityType": "Office hours",
            "ContactMethodType": "Website",
            "ContactValue": dos_service.web},
            {
            "ContactType": "Primary",
            "ContactAvailabilityType": "Office hours",
            "ContactMethodType": "Telephone",
            "ContactValue": dos_service.publicphone},
        ],
        "OpeningTimes": []
    })
    # Act
    response = get_changes(dos_service, nhs_entity)
    # Assert
    assert {} == response, f"Should return empty dict, actually: {response}"


def test_get_changes_different_changes():
    # Arrange
    website = "changed-website.com"
    postcode = "TA1 TA1"
    phone = "0123456789"
    organisation_name = "changed-organisation-name"
    address1 = "changed-address1"
    address2 = "changed-address2"
    address3 = "changed-address3"
    city = "changed-city"
    county = "changed-county"

    nhs_entity = NHSEntity({
        "Postcode": postcode,
        "OrganisationName": organisation_name,
        "Address1": address1,
        "Address2": address2,
        "Address3": address3,
        "City": city,
        "County": county,
        "Contacts": [{
            "ContactType": "Primary",
            "ContactAvailabilityType": "Office hours",
            "ContactMethodType": "Website",
            "ContactValue": website},
            {
            "ContactType": "Primary",
            "ContactAvailabilityType": "Office hours",
            "ContactMethodType": "Telephone",
            "ContactValue": phone},
        ],
        "OpeningTimes": [],
    })

    dos_service = dummy_dos_service()
    dos_location = dummy_dos_location()
    dos_location.postcode = postcode
    dos_location_cache[dos_location.normal_postcode()] = [dos_location]

    expected_changes = {
        ADDRESS_CHANGE_KEY: [address1, address2, address3, city, county],
        PUBLICNAME_CHANGE_KEY: organisation_name,
        WEBSITE_CHANGE_KEY: website,
        POSTCODE_CHANGE_KEY: postcode,
        PHONE_CHANGE_KEY: phone,
    }
    # Act
    response = get_changes(dos_service, nhs_entity)
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
    assert changes == expected_changes, f"Should return {expected_changes} dict, actually: {changes}"


def test_update_changes_address_to_change_request_if_not_equal_is_equal():
    # Arrange
    changes = {}

    nhs_uk_entity = NHSEntity({})
    nhs_uk_entity.address_lines = [
        "address1"
        "address2"
        "address3"
        "city"
        "county"
        ]

    dos_service = dummy_dos_service()
    dos_service.address = "$".join(nhs_uk_entity.address_lines)
    # Act
    actual_changes = update_changes_with_address(changes, dos_service, nhs_uk_entity)
    # Assert
    assert changes == actual_changes, f"Should return {changes} dict, actually: {actual_changes}"


def test_update_changes_address_to_change_request_if_not_equal_not_equal():
    # Arrange
    nhs_uk_entity = NHSEntity({})
    nhs_uk_entity.address_lines = [
        "address1",
        "address2",
        "address3",
        "city",
        "county"]

    dos_service = dummy_dos_service()
    dos_service.address = "Test RD$Testown$Testshire"

    # Act
    actual_changes = {}
    update_changes_with_address(actual_changes, dos_service, nhs_uk_entity)
    expected_changes = {ADDRESS_CHANGE_KEY: nhs_uk_entity.address_lines}
    # Assert
    assert actual_changes == expected_changes,\
        f"Should return {expected_changes} dict, actually: {actual_changes}"


def test_update_changes_with_opening_times():
    # Arrange
    nhs_uk_entity = NHSEntity(
        {
            "OpeningTimes": [
                {
                    "Weekday": "Friday",
                    "Times": "08:45-17:00",
                    "OpeningTimeType": "General",
                    "AdditionalOpeningDate": "",
                    "IsOpen": True,
                },
                {
                    "Weekday": "Tuesday",
                    "Times": "09:00-17:30",
                    "OpeningTimeType": "Additional",
                    "AdditionalOpeningDate": "Nov 12 2021",
                    "IsOpen": True,
                },
            ],
        }
    )
    expected_changes = {
        OPENING_DATES_KEY: {"2021-11-12": [{"start_time": "09:00", "end_time": "17:30"}]},
        OPENING_DAYS_KEY: {
            "Monday": [],
            "Tuesday": [],
            "Wednesday": [],
            "Thursday": [],
            "Friday": [{"start_time": "08:45", "end_time": "17:00"}],
            "Saturday": [],
            "Sunday": [],
        },
    }
    dos_service = dummy_dos_service()
    # Act
    changes = {}
    update_changes_with_opening_times(changes, dos_service, nhs_uk_entity)
    # Assert
    assert expected_changes == changes, f"Should return {expected_changes} dict, actually: {changes}"
