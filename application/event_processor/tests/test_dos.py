from datetime import datetime, timezone, date, time
from os import environ
from random import choices
from unittest.mock import patch
import pytest

from ..dos import (
    DoSService,
    DoSLocation,
    get_matching_dos_services,
    get_specified_opening_times_from_db,
    get_standard_opening_times_from_db,
    get_dos_locations,
)
from .conftest import dummy_dos_location, dummy_dos_service
from opening_times import OpenPeriod, StandardOpeningTimes


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
    test_name = "Test Public Name"
    dos_service = dummy_dos_service()
    dos_service.uid = 1
    dos_service.odscode = "FXXX1"
    dos_service.typeid = 1
    dos_service.statusid = 1
    dos_service.publicname = test_name
    # Assert
    assert test_name in str(dos_service), f"Should return '{test_name}' in string, actually: {dos_service}"


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
    assert "Test Name" in str(dos_service), f"Should return 'Test Name' in string, actually: {dos_service}"


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
    assert "NO-VALID-NAME" in str(dos_service), f"Should return 'NO-VALID-NAME' in string, actually: {dos_service}"


@patch("psycopg2.connect")
def test_get_matching_dos_services_services_returned(mock_connect):
    # Arrange
    odscode = "FQ038"
    environ["DB_SERVER"] = server = "test.db"
    environ["DB_PORT"] = port = "5432"
    environ["DB_NAME"] = db_name = "my-db"
    environ["DB_SCHEMA"] = db_schema = "db_schema"
    environ["DB_USER_NAME"] = db_user = "my-user"
    environ["DB_PASSWORD"] = db_password = "my-password"
    db_return = [
        (
            22851351399,
            "159514725",
            "My Pharmacy",
            odscode,
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

    # Act
    response = get_matching_dos_services("FQ038%")
    # Assert
    service = response[0]
    assert service.odscode == odscode
    assert service.id == 22851351399
    assert service.name == "My Pharmacy"

    mock_connect.assert_called_with(
        host=server,
        port=port,
        dbname=db_name,
        user=db_user,
        options=f"-c search_path=dbo,{db_schema}",
        password=db_password,
        connect_timeout=30,
    )
    mock_connect().cursor().execute.assert_called_with(
        "SELECT id, uid, name, odscode, address, town, postcode, web, email, "
        "fax, nonpublicphone, typeid, parentid, subregionid, statusid, "
        "createdtime, modifiedtime, publicphone, publicname "
        f"FROM services WHERE odscode LIKE '{odscode}%'"
    )
    # Clean up
    del environ["DB_SERVER"]
    del environ["DB_PORT"]
    del environ["DB_NAME"]
    del environ["DB_SCHEMA"]
    del environ["DB_USER_NAME"]
    del environ["DB_PASSWORD"]


@patch("psycopg2.connect")
def test_get_matching_dos_services_no_services_returned(mock_connect):
    # Arrange
    environ["DB_SERVER"] = server = "test.db"
    environ["DB_PORT"] = port = "5432"
    environ["DB_NAME"] = db_name = "my-db"
    environ["DB_SCHEMA"] = db_schema = "db_schema"
    environ["DB_USER_NAME"] = db_user = "my-user"
    environ["DB_PASSWORD"] = db_password = "my-password"
    mock_connect().cursor().fetchall.return_value = []
    odscode = "FQ038"
    expected_response = []
    # Act
    response = get_matching_dos_services(odscode)
    # Assert
    mock_connect.assert_called_with(
        host=server,
        port=port,
        dbname=db_name,
        user=db_user,
        password=db_password,
        options=f"-c search_path=dbo,{db_schema}",
        connect_timeout=30,
    )
    mock_connect().cursor().execute.assert_called_with(
        "SELECT id, uid, name, odscode, address, town, postcode, web, email, "
        "fax, nonpublicphone, typeid, parentid, subregionid, statusid, "
        "createdtime, modifiedtime, publicphone, publicname "
        f"FROM services WHERE odscode LIKE '{odscode}%'"
    )
    assert expected_response == response, f"Should return {expected_response} string, actually: {response}"
    # Clean up
    del environ["DB_SERVER"]
    del environ["DB_PORT"]
    del environ["DB_NAME"]
    del environ["DB_SCHEMA"]
    del environ["DB_USER_NAME"]
    del environ["DB_PASSWORD"]


@patch("psycopg2.connect")
def test_get_specified_opening_times_from_db_times_returned(mock_connect):
    # Arrange
    environ["DB_SERVER"] = server = "test.db"
    environ["DB_PORT"] = port = "5432"
    environ["DB_NAME"] = db_name = "my-db"
    environ["DB_SCHEMA"] = db_schema = "db_schema"
    environ["DB_USER_NAME"] = db_user = "my-user"
    environ["DB_PASSWORD"] = db_password = "my-password"
    db_return = [
        (28334, date(2019, 5, 6), time(8, 0, 0), time(20, 0, 0), False),
        (28334, date(2019, 5, 27), time(8, 0, 0), time(20, 0, 0), False),
        (28334, date(2019, 8, 26), time(8, 0, 0), time(20, 0, 0), False),
    ]
    mock_connect().cursor().fetchall.return_value = db_return
    service_id = 123456
    expected_responses_set = sorted(
        [
            "<SpecifiedOpenTime: 06-05-2019 open=True [08:00:00-20:00:00]>",
            "<SpecifiedOpenTime: 27-05-2019 open=True [08:00:00-20:00:00]>",
            "<SpecifiedOpenTime: 26-08-2019 open=True [08:00:00-20:00:00]>",
        ]
    )
    # Act
    responses = get_specified_opening_times_from_db(service_id)
    responses_str = sorted([str(s) for s in responses])
    # Assert
    assert (
        responses_str == expected_responses_set
    ), f"Should return {expected_responses_set} string, actually: {responses_str}"

    mock_connect.assert_called_with(
        host=server,
        port=port,
        dbname=db_name,
        user=db_user,
        options=f"-c search_path=dbo,{db_schema}",
        password=db_password,
        connect_timeout=30,
    )

    mock_connect().cursor().execute.assert_called_with(
        "SELECT ssod.serviceid, ssod.date, ssot.starttime, ssot.endtime, ssot.isclosed "
        "FROM servicespecifiedopeningdates ssod "
        "INNER JOIN servicespecifiedopeningtimes ssot "
        "ON ssod.serviceid = ssot.servicespecifiedopeningdateid "
        f"WHERE ssod.serviceid = {service_id}"
    )

    # Clean up
    del environ["DB_SERVER"]
    del environ["DB_PORT"]
    del environ["DB_NAME"]
    del environ["DB_SCHEMA"]
    del environ["DB_USER_NAME"]
    del environ["DB_PASSWORD"]


@patch("psycopg2.connect")
def test_get_standard_opening_times_from_db_times_returned(mock_connect):
    # Arrange
    environ["DB_SERVER"] = server = "test.db"
    environ["DB_PORT"] = port = "5432"
    environ["DB_NAME"] = db_name = "my-db"
    environ["DB_SCHEMA"] = db_schema = "db_schema"
    environ["DB_USER_NAME"] = db_user = "my-user"
    environ["DB_PASSWORD"] = db_password = "my-password"
    db_return = [
        (28334, 1, "Tuesday", time(8, 0, 0), time(17, 0, 0)),
        (28334, 1, "Friday", time(9, 0, 0), time(11, 30, 0)),
        (28334, 1, "Friday", time(13, 0, 0), time(15, 30, 0)),
    ]
    mock_connect().cursor().fetchall.return_value = db_return
    service_id = 123456

    expected_std_opening_times = StandardOpeningTimes()
    expected_std_opening_times.add_open_period(OpenPeriod(time(8, 0, 0), time(17, 0, 0)), "tuesday")
    expected_std_opening_times.add_open_period(OpenPeriod(time(9, 0, 0), time(11, 30, 0)), "friday")
    expected_std_opening_times.add_open_period(OpenPeriod(time(13, 0, 0), time(15, 30, 0)), "friday")

    # Act
    response = get_standard_opening_times_from_db(service_id)
    # Assert
    assert (
        response == expected_std_opening_times
    ), f"Should return {expected_std_opening_times} string, actually: {response}"

    mock_connect.assert_called_with(
        host=server,
        port=port,
        dbname=db_name,
        user=db_user,
        options=f"-c search_path=dbo,{db_schema}",
        password=db_password,
        connect_timeout=30,
    )

    # Clean up
    del environ["DB_SERVER"]
    del environ["DB_PORT"]
    del environ["DB_NAME"]
    del environ["DB_SCHEMA"]
    del environ["DB_USER_NAME"]
    del environ["DB_PASSWORD"]


@patch("psycopg2.connect")
def test_get_specified_opening_times_from_db_no_services_returned(mock_connect):
    # Arrange
    environ["DB_SERVER"] = server = "test.db"
    environ["DB_PORT"] = port = "5432"
    environ["DB_NAME"] = db_name = "my-db"
    environ["DB_SCHEMA"] = db_schema = "db_schema"
    environ["DB_USER_NAME"] = db_user = "my-user"
    environ["DB_PASSWORD"] = db_password = "my-password"
    mock_connect().cursor().fetchall.return_value = []
    service_id = 123456
    expected_response = []
    # Act
    response = get_specified_opening_times_from_db(service_id)
    # Assert
    mock_connect.assert_called_with(
        host=server,
        port=port,
        dbname=db_name,
        user=db_user,
        options=f"-c search_path=dbo,{db_schema}",
        password=db_password,
        connect_timeout=30,
    )

    mock_connect().cursor().execute.assert_called_with(
        "SELECT ssod.serviceid, ssod.date, ssot.starttime, ssot.endtime, "
        "ssot.isclosed "
        "FROM servicespecifiedopeningdates ssod "
        "INNER JOIN servicespecifiedopeningtimes ssot "
        "ON ssod.serviceid = ssot.servicespecifiedopeningdateid "
        f"WHERE ssod.serviceid = {service_id}"
    )
    assert expected_response == response, f"Should return {expected_response} string, actually: {response}"
    # Clean up
    del environ["DB_SERVER"]
    del environ["DB_PORT"]
    del environ["DB_NAME"]
    del environ["DB_SCHEMA"]
    del environ["DB_USER_NAME"]
    del environ["DB_PASSWORD"]


@pytest.mark.parametrize(
    "dos_location, expected_result",
    [
        (DoSLocation(id=1, postcode="TE57ER", easting=None, northing=None, latitude=None, longitude=None), False),
        (DoSLocation(id=1, postcode="TE57ER", easting=None, northing=1, latitude=1.1, longitude=1.1), False),
        (DoSLocation(id=1, postcode="TE57ER", easting=1, northing=None, latitude=1.1, longitude=1.1), False),
        (DoSLocation(id=1, postcode="TE57ER", easting=1, northing=1, latitude=None, longitude=1.1), False),
        (DoSLocation(id=1, postcode="TE57ER", easting=1, northing=1, latitude=1.1, longitude=None), False),
        (DoSLocation(id=1, postcode="TE57ER", easting=None, northing=None, latitude=1.1, longitude=1.1), False),
        (DoSLocation(id=1, postcode="TE57ER", easting=1, northing=1, latitude=None, longitude=None), False),
        (DoSLocation(id=1, postcode="TE57ER", easting=1, northing=1, latitude=1.1, longitude=1.1), True),
    ],
)
def test_doslocation_is_valid(dos_location: DoSLocation, expected_result: bool):
    actual_result = dos_location.is_valid()
    assert (
        actual_result is expected_result
    ), f"is_valued check on {dos_location} was found to be {actual_result}, it should be {expected_result}."


@pytest.mark.parametrize(
    "input_postcode, expected_result",
    [
        ("TE57ER", "TE57ER"),
        ("TE5 7ER", "TE57ER"),
        ("T E57ER", "TE57ER"),
        ("T E57E R", "TE57ER"),
        ("T E 5 7 E R", "TE57ER"),
        ("TE57ER  ", "TE57ER"),
        ("   TE57ER", "TE57ER"),
        ("te5 7er", "TE57ER"),
        ("te5  7 e   r", "TE57ER"),
    ],
)
def test_doslocation_normal_postcode(input_postcode: str, expected_result: str):
    dos_location = dummy_dos_location()
    dos_location.postcode = input_postcode
    actual_output = dos_location.normal_postcode()
    assert (
        actual_output == expected_result
    ), f"Normalised postcode for '{input_postcode}' is '{actual_output}', it should be '{expected_result}'."


@patch("psycopg2.connect")
def test_get_dos_locations(mock_connect):
    # Arrange
    environ["DB_SERVER"] = server = "test.db"
    environ["DB_PORT"] = port = "5432"
    environ["DB_NAME"] = db_name = "my-db"
    environ["DB_SCHEMA"] = db_schema = "db_schema"
    environ["DB_USER_NAME"] = db_user = "my-user"
    environ["DB_PASSWORD"] = db_password = "my-password"
    db_return = [{"id": 111, "postcode": "BA2 7AF", "easting": 2, "northing": 3, "latitude": 4.0, "longitude": 2.0}]
    mock_connect().cursor().fetchall.return_value = db_return

    responses = get_dos_locations("BA2 7AF")
    assert len(responses) == 1
    dos_location = responses[0]
    assert dos_location.id == 111
    assert dos_location.postcode == "BA2 7AF"
    assert dos_location.easting == 2
    assert dos_location.northing == 3
    assert dos_location.latitude == 4.0
    assert dos_location.longitude == 2.0

    mock_connect.assert_called_with(
        host=server,
        port=port,
        dbname=db_name,
        user=db_user,
        options=f"-c search_path=dbo,{db_schema}",
        password=db_password,
        connect_timeout=30,
    )

    # Clean up
    del environ["DB_SERVER"]
    del environ["DB_PORT"]
    del environ["DB_NAME"]
    del environ["DB_SCHEMA"]
    del environ["DB_USER_NAME"]
    del environ["DB_PASSWORD"]
