from datetime import datetime, timezone
from os import environ
from random import choices
from unittest.mock import patch

from ..change_request import (
    ADDRESS_CHANGE_KEY,
    PHONE_CHANGE_KEY,
    POSTCODE_CHANGE_KEY,
    PUBLICNAME_CHANGE_KEY,
    WEBSITE_CHANGE_KEY,
)
from ..dos import (
    DoSService,
    add_address_to_change_request_if_not_equal,
    add_field_to_change_request_if_not_equal,
    get_matching_dos_services,
    get_specified_opening_times_from_db,
)
from ..nhs import NHSEntity
from .conftest import dummy_dos_service

FILE_PATH = "application.event_processor.dos"


def test__init__():
    """Pass in random list of values as a mock database row then make sure
    they're correctly set as the attributes of the created object.
    """
    # Arrange
    test_db_row = []
    for column in DoSService.db_columns:
        random_str = "".join(choices("ABCDEFGHIJKLM", k=8))
        test_db_row.append(random_str)
    test_db_row = tuple(test_db_row)
    # Act
    dos_service = DoSService(test_db_row)
    # Assert
    for i, column in enumerate(DoSService.db_columns):
        assert getattr(dos_service, column) == test_db_row[i]


def test__init__publicname():
    # Arrange & Act
    dos_service = dummy_dos_service()
    dos_service.uid = 1
    dos_service.odscode = "FXXX1"
    dos_service.typeid = 1
    dos_service.statusid = 1
    dos_service.publicname = "Test Public Name"
    expected_response = (
        f"<uid={dos_service.uid} ods={dos_service.odscode} type={dos_service.typeid} "
        f"status={dos_service.statusid} name='{dos_service.publicname}'>"
    )
    # Assert
    assert expected_response == str(dos_service), f"Should return {expected_response} string, actually: {dos_service}"


def test__init__name():
    # Arrange & Act
    dos_service = dummy_dos_service()
    dos_service.uid = 1
    dos_service.odscode = "FXXX1"
    dos_service.typeid = 1
    dos_service.statusid = 1
    dos_service.name = "Test Name"
    dos_service.publicname = None
    expected_response = (
        f"<uid={dos_service.uid} ods={dos_service.odscode} type={dos_service.typeid} "
        f"status={dos_service.statusid} name='{dos_service.name}'>"
    )
    # Assert
    assert expected_response == str(dos_service), f"Should return {expected_response} string, actually: {dos_service}"


def test__init__no_name():
    # Arrange & Act
    dos_service = dummy_dos_service()
    dos_service.uid = 1
    dos_service.odscode = "FXXX1"
    dos_service.typeid = 1
    dos_service.statusid = 1
    dos_service.publicname = None
    dos_service.name = None
    expected_response = (
        f"<uid={dos_service.uid} ods={dos_service.odscode} type={dos_service.typeid} "
        f"status={dos_service.statusid} name='NO-VALID-NAME'>"
    )
    # Assert
    assert expected_response == str(dos_service), f"Should return {expected_response} string, actually: {dos_service}"


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
    }
    nhs_entity = NHSEntity(nhs_kwargs)
    # Act
    response = dos_service.get_changes(nhs_entity)
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
    response = dos_service.get_changes(nhs_entity)
    # Assert
    assert expected_changes == response, f"Should return {expected_changes} dict, actually: {response}"


def test_add_field_to_change_request_if_not_equal_is_equal():
    # Arrange
    changes = {}
    nhs_uk_phone = "000000000"
    dos_public_phone = "000000000"
    # Act
    actual_changes = add_field_to_change_request_if_not_equal(changes, "publicphone", dos_public_phone, nhs_uk_phone)
    # Assert
    assert changes == actual_changes, f"Should return {changes} dict, actually: {actual_changes}"


def test_add_field_to_change_request_if_not_equal_not_equal():
    # Arrange
    changes = {}
    nhs_uk_phone = "000000000"
    dos_public_phone = "123456789"
    expected_changes = {"publicphone": nhs_uk_phone}
    # Act
    actual_changes = add_field_to_change_request_if_not_equal(changes, "publicphone", dos_public_phone, nhs_uk_phone)
    # Assert
    assert expected_changes == actual_changes, f"Should return {expected_changes} dict, actually: {actual_changes}"


def test_add_address_to_change_request_if_not_equal_is_equal():
    # Arrange
    changes = {}
    nhs_uk_entity = NHSEntity({})
    nhs_uk_entity.Address1 = "address1"
    nhs_uk_entity.Address2 = "address2"
    nhs_uk_entity.Address3 = "address3"
    nhs_uk_entity.City = "city"
    nhs_uk_entity.County = "county"
    dos_address = (
        f"{nhs_uk_entity.Address1}${nhs_uk_entity.Address2}$"
        f"{nhs_uk_entity.Address3}${nhs_uk_entity.City}${nhs_uk_entity.County}"
    )
    # Act
    actual_changes = add_address_to_change_request_if_not_equal(changes, "address", dos_address, nhs_uk_entity)
    # Assert
    assert changes == actual_changes, f"Should return {changes} dict, actually: {actual_changes}"


def test_add_address_to_change_request_if_not_equal_not_equal():
    # Arrange
    changes = {}
    nhs_uk_entity = NHSEntity({})
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
    actual_changes = add_address_to_change_request_if_not_equal(changes, "address", dos_address, nhs_uk_entity)
    # Assert
    assert expected_changes == actual_changes, f"Should return {changes} dict, actually: {actual_changes}"


@patch(f"{FILE_PATH}.connect")
def test_get_matching_dos_services_services_returned(mock_connect):
    # Arrange
    server = "test.db"
    port = "5432"
    db_name = "my-db"
    db_user = "my-user"
    db_password = "my-password"
    environ["DB_SERVER"] = server
    environ["DB_PORT"] = port
    environ["DB_NAME"] = db_name
    environ["DB_USER_NAME"] = db_user
    environ["DB_PASSWORD"] = db_password
    db_return = [
        (
            22851351399,
            "159514725",
            "My Pharmacy",
            "FQ038",
            "80 Street$Town",
            "Town",
            "TES T12",
            None,
            None,
            None,
            None,
            13,
            123486,
            21813557,
            1,
            datetime(2011, 8, 24, 9, 17, 24, tzinfo=timezone.utc),
            datetime(2019, 3, 13, 0, 37, 7, tzinfo=timezone.utc),
            "0123 012 012",
            None,
        ),
    ]
    mock_connect().cursor().fetchall.return_value = db_return
    odscode = "FQ038"
    expected_response = "[<uid=159514725 ods=FQ038 type=13 status=1 name='My Pharmacy'>]"
    # Act
    response = get_matching_dos_services(odscode)
    # Assert
    assert expected_response == str(response), f"Should return {expected_response} string, actually: {response}"
    mock_connect.assert_called_with(
        host=server, port=port, dbname=db_name, user=db_user, password=db_password, connect_timeout=30
    )
    mock_connect().cursor().execute.assert_called_with(
        "SELECT id, uid, name, odscode, address, town, postcode, web, email, fax, nonpublicphone, typeid, "
        "parentid, subregionid, statusid, createdtime, modifiedtime, publicphone, "
        f"publicname FROM services WHERE odscode LIKE '{odscode}%'"
    )
    # Clean up
    del environ["DB_SERVER"]
    del environ["DB_PORT"]
    del environ["DB_NAME"]
    del environ["DB_USER_NAME"]
    del environ["DB_PASSWORD"]


@patch(f"{FILE_PATH}.connect")
def test_get_matching_dos_services_no_services_returned(mock_connect):
    # Arrange
    server = "test.db"
    port = "5432"
    db_name = "my-db"
    db_user = "my-user"
    db_password = "my-password"
    environ["DB_SERVER"] = server
    environ["DB_PORT"] = port
    environ["DB_NAME"] = db_name
    environ["DB_USER_NAME"] = db_user
    environ["DB_PASSWORD"] = db_password
    mock_connect().cursor().fetchall.return_value = []
    odscode = "FQ038"
    expected_response = []
    # Act
    response = get_matching_dos_services(odscode)
    # Assert
    mock_connect.assert_called_with(
        host=server, port=port, dbname=db_name, user=db_user, password=db_password, connect_timeout=30
    )
    mock_connect().cursor().execute.assert_called_with(
        "SELECT id, uid, name, odscode, address, town, postcode, web, email, fax, nonpublicphone, typeid, "
        "parentid, subregionid, statusid, createdtime, modifiedtime, publicphone, "
        f"publicname FROM services WHERE odscode LIKE '{odscode}%'"
    )
    assert expected_response == response, f"Should return {expected_response} string, actually: {response}"
    # Clean up
    del environ["DB_SERVER"]
    del environ["DB_PORT"]
    del environ["DB_NAME"]
    del environ["DB_USER_NAME"]
    del environ["DB_PASSWORD"]

@patch(f"{FILE_PATH}.connect")
def test_get_specified_opening_times_from_db_times_returned(mock_connect):
    # Arrange
    server = "test.db"
    port = "5432"
    db_name = "my-db"
    db_user = "my-user"
    db_password = "my-password"
    environ["DB_SERVER"] = server
    environ["DB_PORT"] = port
    environ["DB_NAME"] = db_name
    environ["DB_USER_NAME"] = db_user
    environ["DB_PASSWORD"] = db_password
    db_return = [
        (
            28334,
            datetime(2019, 5, 6),
            datetime(1970,1,1,8,0,0),
            datetime(1970,1,1,20,0,0),
            False
        ),
        (
            28334,
            datetime(2019, 5, 27),
            datetime(1970,1,1,8,0,0),
            datetime(1970,1,1,20,0,0),
            False
        ),
        (
            28334,
            datetime(2019, 8, 26),
            datetime(1970,1,1,8,0,0),
            datetime(1970,1,1,20,0,0),
            False
        ),
    ]
    mock_connect().cursor().fetchall.return_value = db_return
    odscode = "FQ038"
    expected_response = "[<SpecifiedOpenTime: 2019-05-06 00:00:00 08:00:00-20:00:00>, <SpecifiedOpenTime: 2019-05-27 00:00:00 08:00:00-20:00:00>, <SpecifiedOpenTime: 2019-08-26 00:00:00 08:00:00-20:00:00>]"
    # Act
    response = get_specified_opening_times_from_db(odscode)
    print(response)
    # Assert
    assert expected_response == str(response), f"Should return {expected_response} string, actually: {response}"
    mock_connect.assert_called_with(
        host=server, port=port, dbname=db_name, user=db_user, password=db_password, connect_timeout=30
    )
    mock_connect().cursor().execute.assert_called_with(
        f"select d.serviceid, d.date, t.starttime, t.endtime, t.isclosed from servicespecifiedopeningdates d, servicespecifiedopeningtimes t where d.serviceid  =  t.servicespecifiedopeningdateid and d.serviceid IN (select id from services  where odscode LIKE '{odscode[0:5]}%'"
    )
    # Clean up
    del environ["DB_SERVER"]
    del environ["DB_PORT"]
    del environ["DB_NAME"]
    del environ["DB_USER_NAME"]
    del environ["DB_PASSWORD"]

@patch(f"{FILE_PATH}.connect")
def test_get_specified_opening_times_from_db_no_services_returned(mock_connect):
    # Arrange
    server = "test.db"
    port = "5432"
    db_name = "my-db"
    db_user = "my-user"
    db_password = "my-password"
    environ["DB_SERVER"] = server
    environ["DB_PORT"] = port
    environ["DB_NAME"] = db_name
    environ["DB_USER_NAME"] = db_user
    environ["DB_PASSWORD"] = db_password
    mock_connect().cursor().fetchall.return_value = []
    odscode = "FQ038"
    expected_response = []
    # Act
    response = get_specified_opening_times_from_db(odscode)
    # Assert
    mock_connect.assert_called_with(
        host=server, port=port, dbname=db_name, user=db_user, password=db_password, connect_timeout=30
    )
    mock_connect().cursor().execute.assert_called_with(
        f"select d.serviceid, d.date, t.starttime, t.endtime, t.isclosed from servicespecifiedopeningdates d, servicespecifiedopeningtimes t where d.serviceid  =  t.servicespecifiedopeningdateid and d.serviceid IN (select id from services  where odscode LIKE '{odscode[0:5]}%'"
    )
    assert expected_response == response, f"Should return {expected_response} string, actually: {response}"
    # Clean up
    del environ["DB_SERVER"]
    del environ["DB_PORT"]
    del environ["DB_NAME"]
    del environ["DB_USER_NAME"]
    del environ["DB_PASSWORD"]

