from os import environ
from unittest.mock import ANY, patch
from datetime import datetime, timedelta

import pytest

from common.tests.conftest import dummy_dos_location, dummy_dos_service
from common.dos import dos_location_cache
from common.nhs import NHSEntity
from ..change_request import (
    ADDRESS_CHANGE_KEY,
    ADDRESS_LINES_KEY,
    OPENING_DATES_KEY,
    OPENING_DAYS_KEY,
    PHONE_CHANGE_KEY,
    POSTCODE_CHANGE_KEY,
    WEBSITE_CHANGE_KEY,
)
from ..changes import (
    get_changes,
    update_changes,
    update_changes_with_opening_times,
    update_changes_with_address_and_postcode,
    update_changes_with_website,
)


FILE_PATH = "application.event_processor.changes"


def test_get_changes_same_data():
    # Act
    dos_service = dummy_dos_service()
    dos_service.address = dos_service.address.title()
    nhs_entity = NHSEntity(
        {
            "Postcode": dos_service.postcode,
            "Phone": dos_service.publicphone,
            "OrganisationName": dos_service.publicname,
            "Address1": dos_service.address,
            "Contacts": [
                {
                    "ContactType": "Primary",
                    "ContactAvailabilityType": "Office hours",
                    "ContactMethodType": "Website",
                    "ContactValue": dos_service.web,
                },
                {
                    "ContactType": "Primary",
                    "ContactAvailabilityType": "Office hours",
                    "ContactMethodType": "Telephone",
                    "ContactValue": dos_service.publicphone,
                },
            ],
            "OpeningTimes": [],
        }
    )
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

    nhs_entity = NHSEntity(
        {
            "Postcode": postcode,
            "OrganisationName": organisation_name,
            "Address1": address1,
            "Address2": address2,
            "Address3": address3,
            "City": city,
            "County": county,
            "Contacts": [
                {
                    "ContactType": "Primary",
                    "ContactAvailabilityType": "Office hours",
                    "ContactMethodType": "Website",
                    "ContactValue": website,
                },
                {
                    "ContactType": "Primary",
                    "ContactAvailabilityType": "Office hours",
                    "ContactMethodType": "Telephone",
                    "ContactValue": phone,
                },
            ],
            "OpeningTimes": [],
        }
    )

    dos_service = dummy_dos_service()
    dos_location = dummy_dos_location()
    dos_location.postcode = postcode
    dos_location_cache[dos_location.normal_postcode()] = [dos_location]

    expected_changes = {
        ADDRESS_CHANGE_KEY: {
            ADDRESS_LINES_KEY: [address1.title(), address2.title(), address3.title(), city.title(), county.title()],
            POSTCODE_CHANGE_KEY: nhs_entity.postcode,
        },
        WEBSITE_CHANGE_KEY: website,
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
    # Assert
    assert changes == {}, f"Should return empty dict, actually: {changes}"


@pytest.mark.parametrize(
    "dos_val, nhs_val,expected",
    [
        ("www.test1.com", "www.test2.com", {"website": "www.test2.com"}),
        ("", "www.test2.com", {"website": "www.test2.com"}),
        (None, "www.test2.com", {"website": "www.test2.com"}),
        ("www.test2.com", None, {"website": ""}),
        ("www.test2.com", "", {"website": ""}),
        ("www.test2.com", "www.test2.com", {}),
        ("", None, {}),
        (None, "", {}),
        (None, None, {}),
        (None, "www.Test.com", {"website": "www.test.com"}),
        (None, "www.Test.com/TEST", {"website": "www.test.com/TEST"}),
        (None, "https://www.Test.com", {"website": "https://www.test.com"}),
        (None, "http://www.Test.com", {"website": "http://www.test.com"}),
        (None, "http://www.Test.com/TeST", {"website": "http://www.test.com/TeST"}),
        (None, "www.teset.com/Test?Test=Test", {"website": "www.teset.com/Test?Test=Test"}),
        (None, "https://www.teset.com/Test?Test=Test", {"website": "https://www.teset.com/Test?Test=Test"}),
    ],
)
@patch(f"{FILE_PATH}.log_website_is_invalid")
def test_update_changes_for_website_success(mock_log_website_is_invalid, dos_val, nhs_val, expected):
    # Arrange
    changes = {}
    nhs_uk_entity = NHSEntity({})
    nhs_uk_entity.website = nhs_val
    dos_service = dummy_dos_service()
    dos_service.web = dos_val
    # Act
    update_changes_with_website(changes, dos_service, nhs_uk_entity)
    assert expected == changes, f"Should return {expected}, actually: {changes}"
    mock_log_website_is_invalid.assert_not_called()


@pytest.mark.parametrize(
    "dos_val, nhs_val,expected",
    [("www.test1.com", "Test@gmail.com", {}), ("1", "test@email.com", {}), ("", " ", {}), (None, " ", {})],
)
@patch(f"{FILE_PATH}.log_website_is_invalid")
def test_update_changes_for_website_fail(mock_log_website_is_invalid, dos_val, nhs_val, expected):
    # Arrange
    changes = {}
    nhs_uk_entity = NHSEntity({})
    nhs_uk_entity.website = nhs_val
    dos_service = dummy_dos_service()
    dos_service.web = dos_val
    # Act
    update_changes_with_website(changes, dos_service, nhs_uk_entity)
    assert expected == changes, f"Should return {expected}, actually: {changes}"
    mock_log_website_is_invalid.assert_called_once_with(ANY, nhs_val.lower())


@pytest.mark.parametrize(
    "dos_val, nhs_val,expected",
    [
        ("000000000", "123456789", {"phone": "123456789"}),
        ("", "123456789", {"phone": "123456789"}),
        (None, "123456789", {"phone": "123456789"}),
        ("123456789", None, {"phone": ""}),
        ("123456789", "", {"phone": ""}),
        ("123456789", "123456789", {}),
        ("", None, {}),
        (None, "", {}),
        ("", " ", {}),
        (None, None, {}),
    ],
)
def test_update_changes_for_phone(dos_val, nhs_val, expected):
    # Arrange
    changes = {}
    # Act
    update_changes(changes, PHONE_CHANGE_KEY, dos_val, nhs_val)
    assert changes == expected, f"Should return {expected}, actually: {changes}"


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


@pytest.mark.parametrize(
    "address, expected_address",
    [
        (
            ["3rd Floor", "24 Hour Road", "Green Tye", "Much Hadham", "Herts"],
            ["3Rd Floor", "24 Hour Road", "Green Tye", "Much Hadham", "Herts"],
        ),
        (
            ["3rd floor", "24 hour road", "green tye", "much hadham", "county"],
            ["3Rd Floor", "24 Hour Road", "Green Tye", "Much Hadham", "County"],
        ),
        (
            ["32A unit", "george's road", "green tye", "less hadham", "testerset"],
            ["32A Unit", "George's Road", "Green Tye", "Less Hadham", "Testerset"],
        ),
        (
            ["2ND FLOOR", "85A", "ABCDE", "WOODCHURCH ROAD", "TESTERSHIRE"],
            ["2Nd Floor", "85A", "Abcde", "Woodchurch Road", "Testershire"],
        ),
    ],
)
@patch(f"{FILE_PATH}.get_valid_dos_postcode")
def test_update_changes_with_address_and_postcode_address_change(
    mock_get_valid_dos_postcode, address: list, expected_address: list, change_event
):
    # Arrange
    changes = {}
    nhs_entity = NHSEntity(change_event)
    dos_service = dummy_dos_service()
    nhs_entity.address_lines = address
    mock_get_valid_dos_postcode.return_value = "other"
    # Act
    update_changes_with_address_and_postcode(changes, dos_service, nhs_entity)
    # Assert
    mock_get_valid_dos_postcode.assert_called_once_with(nhs_entity.normal_postcode())
    assert (
        expected_address == changes["address"]["address_lines"]
    ), f'Should return {expected_address}, actually: {changes["address"]["address_lines"]}'


@patch(f"{FILE_PATH}.get_valid_dos_postcode")
def test_do_not_update_address_if_postcode_invalid(mock_get_valid_dos_postcode, change_event):
    # Arrange
    environ["ENV"] = "test"
    nhs_entity = NHSEntity(change_event)
    dos_service = dummy_dos_service()
    mock_get_valid_dos_postcode.return_value = None
    existing_changes = {ADDRESS_CHANGE_KEY: ["address1", "address2", "address3", "city", "county"]}
    # Act
    update_changes_with_address_and_postcode(existing_changes, dos_service, nhs_entity)
    # Assert
    mock_get_valid_dos_postcode.assert_called_once_with(nhs_entity.normal_postcode())
    assert existing_changes == {}, f"Should return empty dict, actually: {existing_changes}"


@patch(f"{FILE_PATH}.get_valid_dos_postcode")
def test_do_not_update_address_if_postcode_invalid_no_address(mock_get_valid_dos_postcode, change_event):
    # Arrange
    environ["ENV"] = "test"
    nhs_entity = NHSEntity(change_event)
    dos_service = dummy_dos_service()
    mock_get_valid_dos_postcode.return_value = None
    existing_changes = {}
    # Act
    update_changes_with_address_and_postcode(existing_changes, dos_service, nhs_entity)
    # Assert
    mock_get_valid_dos_postcode.assert_called_once_with(nhs_entity.normal_postcode())
    assert existing_changes == {}, f"Should return empty dict, actually: {existing_changes}"


@patch(f"{FILE_PATH}.get_valid_dos_postcode")
def test_update_changes_with_address_and_postcode_if_address_is_equal_but_not_postcode(mock_get_valid_dos_postcode):
    # Arrange
    changes = {}

    nhs_uk_entity = NHSEntity({})
    address_lines = ["Address1", "Address2", "Address3", "City", "County"]
    nhs_uk_entity.address_lines = address_lines
    nhs_uk_entity.postcode = "TA2 TA2"

    dos_service = dummy_dos_service()
    dos_service.address = "$".join(nhs_uk_entity.address_lines)
    dos_service.postcode = "TA1 TA1"

    mock_get_valid_dos_postcode.return_value = "TA2TA2"
    expected_changes = {
        "address": {
            "address_lines": address_lines,
            "post_code": "TA2TA2",
        }
    }

    # Act
    update_changes_with_address_and_postcode(changes, dos_service, nhs_uk_entity)
    # Assert
    assert expected_changes == changes, f"Should return {expected_changes} dict, actually: {changes}"


@patch(f"{FILE_PATH}.logger")
@patch(f"{FILE_PATH}.get_valid_dos_postcode")
def test_not_update_changes_with_address_and_postcode_to_change_request_if_address_and_postcode_is_equal(
    mock_get_valid_dos_postcode, mock_logger
):
    # Arrange
    changes = {}

    nhs_uk_entity = NHSEntity({})
    address_lines = ["Address1", "Address2", "Address3", "City", "County"]
    nhs_uk_entity.address_lines = address_lines
    nhs_uk_entity.postcode = "TA2 TA2"

    dos_service = dummy_dos_service()
    dos_service.address = "$".join(nhs_uk_entity.address_lines)
    dos_service.postcode = "TA2 TA2"
    mock_get_valid_dos_postcode.return_value = "TA2 TA2"
    expected_changes = {}

    # Act
    update_changes_with_address_and_postcode(changes, dos_service, nhs_uk_entity)
    # Assert
    assert expected_changes == changes, f"Should return {expected_changes} dict, actually: {changes}"


def test_update_changes_with_opening_times():

    date_now = datetime.now().date()
    date_future_4wks = date_now + timedelta(weeks=4)
    date_future_4wks_2ds = date_now + timedelta(weeks=4, days=2)
    date_future_6wks = date_now + timedelta(weeks=6)
    date_future_8wks = date_now + timedelta(weeks=8)
    date_future_8wks_1ds = date_now + timedelta(weeks=8, days=1)
    date_future_8wks_3ds = date_now + timedelta(weeks=8, days=3)
    date_future_8wks_4ds = date_now + timedelta(weeks=8, days=4)
    date_future_9wks = date_now + timedelta(weeks=9)
    date_future_7wks = date_now + timedelta(weeks=7)
    date_past_2wks = date_now - timedelta(weeks=2)
    # Arrange
    nhs_uk_entity = NHSEntity(
        {
            "OpeningTimes": [
                {
                    "Weekday": "Monday",
                    "OpeningTime": "09:00",
                    "ClosingTime": "12:00",
                    "OpeningTimeType": "General",
                    "AdditionalOpeningDate": "",
                    "IsOpen": True,
                },
                {
                    "Weekday": "Monday",
                    "OpeningTime": "13:00",
                    "ClosingTime": "16:00",
                    "OpeningTimeType": "General",
                    "AdditionalOpeningDate": "",
                    "IsOpen": True,
                },
                {
                    "Weekday": "Monday",
                    "OpeningTime": "17:00",
                    "ClosingTime": "18:00",
                    "OpeningTimeType": "General",
                    "AdditionalOpeningDate": "",
                    "IsOpen": True,
                },
                {
                    "Weekday": "Tuesday",
                    "OpeningTime": "09:00",
                    "ClosingTime": "20:00",
                    "OpeningTimeType": "General",
                    "AdditionalOpeningDate": "",
                    "IsOpen": True,
                },
                {
                    "Weekday": "Wednesday",
                    "OpeningTime": "09:00",
                    "ClosingTime": "20:00",
                    "OpeningTimeType": "General",
                    "AdditionalOpeningDate": "",
                    "IsOpen": True,
                },
                {
                    "Weekday": "Thursday",
                    "OpeningTime": "09:00",
                    "ClosingTime": "20:00",
                    "OpeningTimeType": "General",
                    "AdditionalOpeningDate": "",
                    "IsOpen": True,
                },
                {
                    "Weekday": "Friday",
                    "OpeningTime": "09:00",
                    "ClosingTime": "20:00",
                    "OpeningTimeType": "General",
                    "AdditionalOpeningDate": "",
                    "IsOpen": True,
                },
                {
                    "Weekday": "Saturday",
                    "OpeningTime": "09:00",
                    "ClosingTime": "12:00",
                    "OpeningTimeType": "General",
                    "AdditionalOpeningDate": "",
                    "IsOpen": True,
                },
                {
                    "Weekday": "Saturday",
                    "OpeningTime": "13:00",
                    "ClosingTime": "18:00",
                    "OpeningTimeType": "General",
                    "AdditionalOpeningDate": "",
                    "IsOpen": True,
                },
                {
                    "Weekday": "Sunday",
                    "OpeningTime": None,
                    "ClosingTime": None,
                    "OpeningTimeType": "General",
                    "AdditionalOpeningDate": "",
                    "IsOpen": False,
                },
                {
                    "Weekday": "",
                    "OpeningTime": "08:00",
                    "ClosingTime": "12:00",
                    "OpeningTimeType": "Additional",
                    "AdditionalOpeningDate": date_future_4wks.strftime("%b %d %Y"),
                    "IsOpen": True,
                },
                {
                    "Weekday": "",
                    "OpeningTime": "13:00",
                    "ClosingTime": "16:00",
                    "OpeningTimeType": "Additional",
                    "AdditionalOpeningDate": date_future_4wks.strftime("%b %d %Y"),
                    "IsOpen": True,
                },
                {
                    "Weekday": "",
                    "OpeningTime": "07:00",
                    "ClosingTime": "11:00",
                    "OpeningTimeType": "Additional",
                    "AdditionalOpeningDate": date_future_4wks_2ds.strftime("%b %d %Y"),
                    "IsOpen": True,
                },
                {
                    "Weekday": "",
                    "OpeningTime": "12:00",
                    "ClosingTime": "15:00",
                    "OpeningTimeType": "Additional",
                    "AdditionalOpeningDate": date_future_4wks_2ds.strftime("%b %d %Y"),
                    "IsOpen": True,
                },
                {
                    "Weekday": "",
                    "OpeningTime": "16:00",
                    "ClosingTime": "18:00",
                    "OpeningTimeType": "Additional",
                    "AdditionalOpeningDate": date_future_4wks_2ds.strftime("%b %d %Y"),
                    "IsOpen": True,
                },
                {
                    "Weekday": "",
                    "OpeningTime": None,
                    "ClosingTime": None,
                    "OpeningTimeType": "Additional",
                    "AdditionalOpeningDate": date_future_6wks.strftime("%b %d %Y"),
                    "IsOpen": False,
                },
                {
                    "Weekday": "",
                    "OpeningTime": None,
                    "ClosingTime": None,
                    "OpeningTimeType": "Additional",
                    "AdditionalOpeningDate": date_future_8wks.strftime("%b %d %Y"),
                    "IsOpen": False,
                },
                {
                    "Weekday": "",
                    "OpeningTime": None,
                    "ClosingTime": None,
                    "OpeningTimeType": "Additional",
                    "AdditionalOpeningDate": date_future_8wks_1ds.strftime("%b %d %Y"),
                    "IsOpen": False,
                },
                {
                    "Weekday": "",
                    "OpeningTime": "07:00",
                    "ClosingTime": "12:00",
                    "OpeningTimeType": "Additional",
                    "AdditionalOpeningDate": date_future_8wks_3ds.strftime("%b %d %Y"),
                    "IsOpen": True,
                },
                {
                    "Weekday": "",
                    "OpeningTime": "13:00",
                    "ClosingTime": "17:00",
                    "OpeningTimeType": "Additional",
                    "AdditionalOpeningDate": date_future_8wks_3ds.strftime("%b %d %Y"),
                    "IsOpen": True,
                },
                {
                    "Weekday": "",
                    "OpeningTime": "18:00",
                    "ClosingTime": "20:00",
                    "OpeningTimeType": "Additional",
                    "AdditionalOpeningDate": date_future_8wks_3ds.strftime("%b %d %Y"),
                    "IsOpen": True,
                },
                {
                    "Weekday": "",
                    "OpeningTime": "07:00",
                    "ClosingTime": "12:00",
                    "OpeningTimeType": "Additional",
                    "AdditionalOpeningDate": date_future_8wks_4ds.strftime("%b %d %Y"),
                    "IsOpen": True,
                },
                {
                    "Weekday": "",
                    "OpeningTime": "13:00",
                    "ClosingTime": "17:00",
                    "OpeningTimeType": "Additional",
                    "AdditionalOpeningDate": date_future_8wks_4ds.strftime("%b %d %Y"),
                    "IsOpen": True,
                },
                {
                    "Weekday": "",
                    "OpeningTime": "18:00",
                    "ClosingTime": "20:00",
                    "OpeningTimeType": "Additional",
                    "AdditionalOpeningDate": date_future_8wks_4ds.strftime("%b %d %Y"),
                    "IsOpen": True,
                },
                {
                    "Weekday": "",
                    "OpeningTime": "06:00",
                    "ClosingTime": "12:00",
                    "OpeningTimeType": "Additional",
                    "AdditionalOpeningDate": date_future_9wks.strftime("%b %d %Y"),
                    "IsOpen": True,
                },
                {
                    "Weekday": "",
                    "OpeningTime": "13:00",
                    "ClosingTime": "18:00",
                    "OpeningTimeType": "Additional",
                    "AdditionalOpeningDate": date_future_9wks.strftime("%b %d %Y"),
                    "IsOpen": True,
                },
                {
                    "Weekday": "",
                    "OpeningTime": None,
                    "ClosingTime": None,
                    "OpeningTimeType": "Additional",
                    "AdditionalOpeningDate": date_future_7wks.strftime("%b %d %Y"),
                    "IsOpen": False,
                },
                {
                    "Weekday": "",
                    "OpeningTime": "12:00",
                    "ClosingTime": "18:00",
                    "OpeningTimeType": "Additional",
                    "AdditionalOpeningDate": date_past_2wks.strftime("%b %d %Y"),
                    "IsOpen": True,
                },
            ],
        }
    )

    expected_changes = {
        OPENING_DATES_KEY: {
            date_future_4wks.strftime("%Y-%m-%d"): [
                {"start_time": "08:00", "end_time": "12:00"},
                {"start_time": "13:00", "end_time": "16:00"},
            ],
            date_future_4wks_2ds.strftime("%Y-%m-%d"): [
                {"start_time": "07:00", "end_time": "11:00"},
                {"start_time": "12:00", "end_time": "15:00"},
                {"start_time": "16:00", "end_time": "18:00"},
            ],
            date_future_6wks.strftime("%Y-%m-%d"): [],
            date_future_8wks.strftime("%Y-%m-%d"): [],
            date_future_8wks_1ds.strftime("%Y-%m-%d"): [],
            date_future_8wks_3ds.strftime("%Y-%m-%d"): [
                {"start_time": "07:00", "end_time": "12:00"},
                {"start_time": "13:00", "end_time": "17:00"},
                {"start_time": "18:00", "end_time": "20:00"},
            ],
            date_future_8wks_4ds.strftime("%Y-%m-%d"): [
                {"start_time": "07:00", "end_time": "12:00"},
                {"start_time": "13:00", "end_time": "17:00"},
                {"start_time": "18:00", "end_time": "20:00"},
            ],
            date_future_9wks.strftime("%Y-%m-%d"): [
                {"start_time": "06:00", "end_time": "12:00"},
                {"start_time": "13:00", "end_time": "18:00"},
            ],
            date_future_7wks.strftime("%Y-%m-%d"): [],
        },
        OPENING_DAYS_KEY: {
            "Monday": [
                {"start_time": "09:00", "end_time": "12:00"},
                {"start_time": "13:00", "end_time": "16:00"},
                {"start_time": "17:00", "end_time": "18:00"},
            ],
            "Tuesday": [{"start_time": "09:00", "end_time": "20:00"}],
            "Wednesday": [{"start_time": "09:00", "end_time": "20:00"}],
            "Thursday": [{"start_time": "09:00", "end_time": "20:00"}],
            "Friday": [{"start_time": "09:00", "end_time": "20:00"}],
            "Saturday": [{"start_time": "09:00", "end_time": "12:00"}, {"start_time": "13:00", "end_time": "18:00"}],
            "Sunday": [],
        },
    }
    dos_service = dummy_dos_service()
    # Act
    changes = {}
    update_changes_with_opening_times(changes, dos_service, nhs_uk_entity)
    # Assert
    assert expected_changes == changes, f"Should return {expected_changes} dict, actually: {changes}"
