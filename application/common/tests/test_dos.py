from datetime import date, datetime, time, timezone
from random import choices
from unittest.mock import MagicMock, patch
import pytest

from .conftest import dummy_dos_location, dummy_dos_service
from common.constants import DENTIST_ORG_TYPE_ID, PHARMACY_ORG_TYPE_ID
from ..opening_times import OpenPeriod, StandardOpeningTimes
from ..dos import (
    DoSLocation,
    DoSService,
    get_dos_locations,
    get_matching_dos_services,
    get_specified_opening_times_from_db,
    get_standard_opening_times_from_db,
)

FILE_PATH = "application.common.dos"


def test_field_names():
    assert DoSService.field_names() == [
        "id",
        "uid",
        "name",
        "odscode",
        "address",
        "town",
        "postcode",
        "web",
        "email",
        "fax",
        "nonpublicphone",
        "typeid",
        "parentid",
        "subregionid",
        "statusid",
        "createdtime",
        "modifiedtime",
        "publicphone",
        "publicname",
        "servicename",
    ]


def test__init__():
    """Pass in random list of values as a mock database row then make sure
    they're correctly set as the attributes of the created object.
    """
    # Arrange
    test_db_row = {}
    for column in DoSService.field_names():
        random_str = "".join(choices("ABCDEFGHIJKLM", k=8))
        test_db_row[column] = random_str
    # Act
    dos_service = DoSService(test_db_row)
    # Assert
    for field_name in DoSService.field_names():
        assert getattr(dos_service, field_name) == test_db_row[field_name]


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


@patch(f"{FILE_PATH}.query_dos_db")
def test_get_matching_dos_services_pharmacy_services_returned(mock_query_dos_db):
    # Arrange
    odscode = "FQ038"
    name = "My Pharmacy"
    db_return = get_db_item(odscode, name)
    mock_connection = MagicMock()
    mock_connection.fetchall.return_value = db_return
    mock_query_dos_db.return_value = mock_connection
    # Act
    response = get_matching_dos_services(odscode, PHARMACY_ORG_TYPE_ID)
    # Assert
    service = response[0]
    assert service.odscode == odscode
    assert service.id == 22851351399
    assert service.name == name
    mock_query_dos_db.assert_called_once_with(
        query=(
            "SELECT s.id, uid, s.name, odscode, address, town, postcode, web, email, fax, nonpublicphone, typeid,"
            " parentid, subregionid, statusid, createdtime, modifiedtime, publicphone, publicname, st.name servicename"
            " FROM services s LEFT JOIN servicetypes st ON s.typeid = st.id"
            " WHERE odscode LIKE %(ODS)s"
        ),
        vars={"ODS": f"{odscode[0:5]}%"},
    )
    mock_connection.fetchall.assert_called_with()
    mock_connection.close.assert_called_with()


def test_any_generic_bankholiday_open_periods():
    dos_service = dummy_dos_service()
    dos_service._standard_opening_times = StandardOpeningTimes()
    op1 = OpenPeriod(time(8, 0, 0), time(13, 0, 0))
    op2 = OpenPeriod(time(14, 0, 0), time(18, 0, 0))

    assert dos_service.any_generic_bankholiday_open_periods() is False

    dos_service._standard_opening_times.add_open_period(op1, "monday")
    assert dos_service.any_generic_bankholiday_open_periods() is False

    dos_service._standard_opening_times.add_open_period(op2, "monday")
    assert dos_service.any_generic_bankholiday_open_periods() is False

    dos_service._standard_opening_times.add_open_period(op1, "tuesday")
    dos_service._standard_opening_times.add_open_period(op1, "wednesday")
    dos_service._standard_opening_times.add_open_period(op1, "thursday")
    dos_service._standard_opening_times.add_open_period(op1, "friday")
    dos_service._standard_opening_times.add_open_period(op1, "saturday")
    dos_service._standard_opening_times.add_open_period(op1, "sunday")
    assert dos_service.any_generic_bankholiday_open_periods() is False

    dos_service._standard_opening_times.add_open_period(op1, "bankholiday")
    assert dos_service.any_generic_bankholiday_open_periods()

    dos_service._standard_opening_times.add_open_period(op2, "bankholiday")
    assert dos_service.any_generic_bankholiday_open_periods()

    dos_service._standard_opening_times.generic_bankholiday = []
    assert dos_service.any_generic_bankholiday_open_periods() is False


@patch(f"{FILE_PATH}.query_dos_db")
def test_get_matching_dos_services_dentist_services_returned(mock_query_dos_db):
    # Arrange
    odscode = "V00393a"
    name = "My Dental Practice"
    db_return = get_db_item(odscode, name)
    mock_connection = MagicMock()
    mock_connection.fetchall.return_value = db_return
    mock_query_dos_db.return_value = mock_connection
    ods6_code = "V0393a"
    # Act
    response = get_matching_dos_services(odscode, DENTIST_ORG_TYPE_ID)
    # Assert
    service = response[0]
    assert service.odscode == odscode
    assert service.id == 22851351399
    assert service.name == name
    mock_query_dos_db.assert_called_once_with(
        query=(
            "SELECT s.id, uid, s.name, odscode, address, town, postcode, web, email, fax, nonpublicphone, typeid,"
            " parentid, subregionid, statusid, createdtime, modifiedtime, publicphone, publicname, st.name servicename"
            " FROM services s LEFT JOIN servicetypes st ON s.typeid = st.id"
            " WHERE odscode = %(ODS)s or odscode LIKE %(ODS7)s"
        ),
        vars={"ODS": f"{ods6_code}", "ODS7": f"{odscode}%"},
    )
    mock_connection.fetchall.assert_called_with()
    mock_connection.close.assert_called_with()


@patch(f"{FILE_PATH}.query_dos_db")
def test_get_matching_dos_services_no_services_returned(mock_query_dos_db):
    # Arrange
    odscode = "FQ038"
    db_return = []
    mock_connection = MagicMock()
    mock_connection.fetchall.return_value = db_return
    mock_query_dos_db.return_value = mock_connection
    # Act
    response = get_matching_dos_services(odscode, PHARMACY_ORG_TYPE_ID)
    # Assert
    assert response == []
    mock_query_dos_db.assert_called_once_with(
        query=(
            "SELECT s.id, uid, s.name, odscode, address, town, postcode, web, email, fax, nonpublicphone, typeid,"
            " parentid, subregionid, statusid, createdtime, modifiedtime, publicphone, publicname, st.name servicename"
            " FROM services s LEFT JOIN servicetypes st ON s.typeid = st.id"
            " WHERE odscode LIKE %(ODS)s"
        ),
        vars={"ODS": f"{odscode[0:5]}%"},
    )
    mock_connection.fetchall.assert_called_with()
    mock_connection.close.assert_called_with()


@patch(f"{FILE_PATH}.query_dos_db")
def test_get_specified_opening_times_from_db_times_returned(mock_query_dos_db):
    # Arrange
    mock_connection = MagicMock()
    db_return = [
        (28334, date(2019, 5, 6), time(8, 0, 0), time(20, 0, 0), False),
        (28334, date(2019, 5, 27), time(8, 0, 0), time(20, 0, 0), False),
        (28334, date(2019, 8, 26), time(8, 0, 0), time(20, 0, 0), False),
        (28334, date(2019, 8, 26), time(21, 0, 0), time(22, 0, 0), False),
        (28334, date(2019, 9, 20), time(0, 0, 0), time(0, 0, 0), True),
        (28334, date(2019, 9, 21), time(14, 30, 0), time(16, 0, 0), True),
        (28334, date(2019, 5, 6), time(6, 0, 0), time(7, 0, 0), False),
    ]
    mock_connection.fetchall.return_value = db_return
    mock_query_dos_db.return_value = mock_connection
    service_id = 123456
    expected_responses_set = sorted(
        [
            "<SpecifiedOpenTime: 06-05-2019 open=True [06:00:00-07:00:00, 08:00:00-20:00:00]>",
            "<SpecifiedOpenTime: 27-05-2019 open=True [08:00:00-20:00:00]>",
            "<SpecifiedOpenTime: 26-08-2019 open=True [08:00:00-20:00:00, 21:00:00-22:00:00]>",
            "<SpecifiedOpenTime: 20-09-2019 open=False []>",
            "<SpecifiedOpenTime: 21-09-2019 open=False []>",
        ]
    )
    # Act
    responses = get_specified_opening_times_from_db(service_id)
    responses_str = sorted([str(s) for s in responses])
    # Assert
    assert (
        responses_str == expected_responses_set
    ), f"Should return {expected_responses_set} string, actually: {responses_str}"

    mock_query_dos_db.assert_called_once_with(
        "SELECT ssod.serviceid, ssod.date, ssot.starttime, ssot.endtime, ssot.isclosed "
        "FROM servicespecifiedopeningdates ssod "
        "INNER JOIN servicespecifiedopeningtimes ssot "
        "ON ssod.id = ssot.servicespecifiedopeningdateid "
        "WHERE ssod.serviceid = %(service_id)s",
        {"service_id": service_id},
    )


@patch(f"{FILE_PATH}.query_dos_db")
def test_get_standard_opening_times_from_db_times_returned(mock_query_dos_db):
    # Arrange
    db_return = [
        (28334, 1, "Tuesday", time(8, 0, 0), time(17, 0, 0)),
        (28334, 1, "Friday", time(9, 0, 0), time(11, 30, 0)),
        (28334, 1, "Friday", time(13, 0, 0), time(15, 30, 0)),
    ]
    mock_connection = MagicMock()
    service_id = 123456
    mock_connection.fetchall.return_value = db_return
    mock_query_dos_db.return_value = mock_connection
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

    mock_query_dos_db.assert_called_once_with(
        "SELECT sdo.serviceid, sdo.dayid, otd.name, sdot.starttime, sdot.endtime "
        "FROM servicedayopenings sdo "
        "INNER JOIN servicedayopeningtimes sdot "
        "ON sdo.id = sdot.servicedayopeningid "
        "LEFT JOIN openingtimedays otd "
        "ON sdo.dayid = otd.id "
        "WHERE sdo.serviceid = %(service_id)s",
        {"service_id": service_id},
    )


@patch(f"{FILE_PATH}.query_dos_db")
def test_get_specified_opening_times_from_db_no_times_returned(mock_query_dos_db):
    # Arrange
    mock_connection = MagicMock()
    db_return = []
    mock_connection.fetchall.return_value = db_return
    mock_query_dos_db.return_value = mock_connection
    service_id = 123456
    expected_responses_set = sorted([])
    # Act
    responses = get_specified_opening_times_from_db(service_id)
    responses_str = sorted([str(s) for s in responses])
    # Assert
    assert (
        responses_str == expected_responses_set
    ), f"Should return {expected_responses_set} string, actually: {responses_str}"

    mock_query_dos_db.assert_called_once_with(
        "SELECT ssod.serviceid, ssod.date, ssot.starttime, ssot.endtime, ssot.isclosed "
        "FROM servicespecifiedopeningdates ssod "
        "INNER JOIN servicespecifiedopeningtimes ssot "
        "ON ssod.id = ssot.servicespecifiedopeningdateid "
        "WHERE ssod.serviceid = %(service_id)s",
        {"service_id": service_id},
    )


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


@patch(f"{FILE_PATH}.query_dos_db")
def test_get_dos_locations(mock_query_dos_db):
    # Arrange
    mock_connection = MagicMock()
    postcode = "BA2 7AF"
    db_return = [{"id": 111, "postcode": postcode, "easting": 2, "northing": 3, "latitude": 4.0, "longitude": 2.0}]
    mock_connection.fetchall.return_value = db_return
    mock_query_dos_db.return_value = mock_connection

    # Act
    responses = get_dos_locations(postcode)
    # Assert
    assert len(responses) == 1
    dos_location = responses[0]
    assert dos_location.id == 111
    assert dos_location.postcode == postcode
    assert dos_location.easting == 2
    assert dos_location.northing == 3
    assert dos_location.latitude == 4.0
    assert dos_location.longitude == 2.0

    mock_query_dos_db.assert_called_once_with(
        "SELECT id, postcode, easting, northing, latitude, longitude, postaltown "
        "FROM locations WHERE postcode ~* %(pc_regex)s",
        {"pc_regex": " *".join(postcode.replace(" ", "").upper())},
    )


def get_db_item(odscode, name):
    return [
        {
            "id": 22851351399,
            "uid": "159514725",
            "name": name,
            "odscode": odscode,
            "address": "80 Street$Town",
            "town": "Town",
            "postcode": "TES T12",
            "web": None,
            "email": None,
            "fax": None,
            "nonpublicphone": None,
            "typeid": 13,
            "parentid": 123486,
            "subregionid": 21813557,
            "statusid": 1,
            "createdtime": datetime(2011, 8, 24, 9, 17, 24, tzinfo=timezone.utc),
            "modifiedtime": datetime(2019, 3, 13, 0, 37, 7, tzinfo=timezone.utc),
            "publicphone": "0123 012 012",
            "publicname": None,
            "servicename": "my service",
        }
    ]
