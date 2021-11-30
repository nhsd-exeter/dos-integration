from datetime import datetime, timezone
from os import environ
from random import choices
from unittest.mock import patch
from ..dos import (
    DoSService,
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


def test__init__public_name():
    # Arrange & Act
    dos_service = dummy_dos_service()
    dos_service.uid = 1
    dos_service.odscode = "FXXX1"
    dos_service.typeid = 1
    dos_service.statusid = 1
    dos_service.publicname = "Test Public Name"
    # Assert
    assert ("Test Public Name" in str(dos_service), 
            f"Should return 'Test Public Name' in string, actually: {dos_service}")


def test__init__name():
    # Arrange & Act
    dos_service = dummy_dos_service()
    dos_service.uid = 1
    dos_service.odscode = "FXXX1"
    dos_service.typeid = 1
    dos_service.statusid = 1
    dos_service.name = "Test Name"
    dos_service.publicname = None
    # Assert
    assert ("Test Name" in str(dos_service), 
            f"Should return 'Test Name' in string, actually: {dos_service}")


def test__init__no_name():
    # Arrange & Act
    dos_service = dummy_dos_service()
    dos_service.uid = 1
    dos_service.odscode = "FXXX1"
    dos_service.typeid = 1
    dos_service.statusid = 1
    dos_service.publicname = None
    dos_service.name = None
    # Assert
    assert ("NO-VALID-NAME" in str(dos_service), 
            f"Should return 'NO-VALID-NAME' in string, actually: {dos_service}")



@patch(f"{FILE_PATH}.connect")
def test_get_matching_dos_services_services_returned(mock_connect):
    # Arrange
    environ["DB_SERVER"] = server = "test.db"
    environ["DB_PORT"] = port = "5432"
    environ["DB_NAME"] = db_name = "my-db"
    environ["DB_USER_NAME"] = db_user = "my-user"
    environ["DB_PASSWORD"] = db_password = "my-password"
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
    expected_response = "[<DoSService: uid=159514725 ods=FQ038 type=13 status=1 name='My Pharmacy'>]"
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
    environ["DB_SERVER"] = server = "test.db"
    environ["DB_PORT"] = port = "5432"
    environ["DB_NAME"] = db_name = "my-db"
    environ["DB_USER_NAME"] = db_user = "my-user"
    environ["DB_PASSWORD"] = db_password = "my-password"
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
    service_id = 123456
    expected_response = "[<SpecifiedOpenTime: 2019-05-06 [08:00-20:00]>, <SpecifiedOpenTime: 2019-05-27 [08:00-20:00]>, <SpecifiedOpenTime: 2019-08-26 [08:00-20:00]>]"
    # Act
    response = get_specified_opening_times_from_db(service_id)
    # Assert
    assert expected_response == str(response), f"Should return {expected_response} string, actually: {response}"
    mock_connect.assert_called_with(
        host=server, port=port, dbname=db_name, user=db_user, password=db_password, connect_timeout=30
    )
    mock_connect().cursor().execute.assert_called_with("SELECT ssod.serviceid, ssod.date, ssot.starttime, ssot.endtime, ssot.isclosed FROM servicespecifiedopeningdates ssod "
                    "LEFT JOIN servicespecifiedopeningtimes ssot ON ssod.serviceid = ssot.servicespecifiedopeningdateid "
                    f"WHERE ssod.serviceid = {service_id}"
        
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
    service_id = 123456
    expected_response = []
    # Act
    response = get_specified_opening_times_from_db(service_id)
    # Assert
    mock_connect.assert_called_with(
        host=server, port=port, dbname=db_name, user=db_user, password=db_password, connect_timeout=30
    )
    mock_connect().cursor().execute.assert_called_with("SELECT ssod.serviceid, ssod.date, ssot.starttime, ssot.endtime, ssot.isclosed FROM servicespecifiedopeningdates ssod "
                    "LEFT JOIN servicespecifiedopeningtimes ssot ON ssod.serviceid = ssot.servicespecifiedopeningdateid "
                    f"WHERE ssod.serviceid = {service_id}"
    )
    assert expected_response == response, f"Should return {expected_response} string, actually: {response}"
    # Clean up
    del environ["DB_SERVER"]
    del environ["DB_PORT"]
    del environ["DB_NAME"]
    del environ["DB_USER_NAME"]
    del environ["DB_PASSWORD"]

