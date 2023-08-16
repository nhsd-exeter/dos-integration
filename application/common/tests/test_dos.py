from datetime import date, datetime, time, timezone
from random import choices
from unittest.mock import MagicMock, patch

from application.common.dos import (
    ACTIVE_STATUS_ID,
    DoSService,
    db_rows_to_spec_open_times,
    db_rows_to_spec_open_times_map,
    db_rows_to_std_open_times,
    db_rows_to_std_open_times_map,
    get_dos_locations,
    get_matching_dos_services,
    get_region,
    get_specified_opening_times_from_db,
    get_standard_opening_times_from_db,
    get_valid_dos_location,
    has_palliative_care,
)
from application.common.opening_times import OpenPeriod, SpecifiedOpeningTime, StandardOpeningTimes
from application.conftest import dummy_dos_service
from common.constants import (
    DOS_PALLIATIVE_CARE_SYMPTOM_DISCRIMINATOR,
    DOS_PALLIATIVE_CARE_SYMPTOM_GROUP,
)

OP = OpenPeriod.from_string
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
        "typeid",
        "statusid",
        "status_name",
        "publicphone",
        "publicname",
        "service_type_name",
        "easting",
        "northing",
        "latitude",
        "longitude",
        "region",
    ]


def test__init__():
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


def test_dos_service_get_region():
    # Arrange
    dos_service = dummy_dos_service()
    dos_service.region = "Test Region"
    # Act
    region = dos_service.get_region()
    # Assert
    assert region == "Test Region"


@patch(f"{FILE_PATH}.get_region")
def test_dos_service_get_region_if_none(mock_get_region: MagicMock) -> None:
    # Arrange
    dos_service = dummy_dos_service()
    dos_service.region = ""
    mock_get_region.return_value = region_value = "Test Region"
    # Act
    region = dos_service.get_region()
    # Assert
    assert region == region_value
    mock_get_region.assert_called_once()


@patch(f"{FILE_PATH}.connect_to_dos_db_replica")
@patch(f"{FILE_PATH}.query_dos_db")
def test_get_matching_dos_services_pharmacy_services_returned(mock_query_dos_db, mock_connect_to_dos_db_replica):
    # Arrange
    odscode = "FQ038"
    name = "My Pharmacy"
    service_id = 22851351399
    db_return = [get_db_item(odscode, name, id=service_id)]
    mock_connection = MagicMock()
    mock_connect_to_dos_db_replica.return_value.__enter__.return_value = mock_connection
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = db_return
    mock_query_dos_db.return_value = mock_cursor
    # Act
    response = get_matching_dos_services(odscode, False)
    # Assert
    service = response[0]
    assert service.odscode == odscode
    assert service.id == service_id
    assert service.name == name
    mock_query_dos_db.assert_called_once_with(
        connection=mock_connection,
        query=(
            "SELECT s.id, uid, s.name, odscode, address, postcode, web, typeid,"
            "statusid, ss.name status_name, publicphone, publicname, st.name service_type_name "
            "FROM services s LEFT JOIN servicetypes st ON s.typeid = st.id "
            "LEFT JOIN servicestatuses ss on s.statusid = ss.id "
            "WHERE s.odscode LIKE %(ODS)s AND s.typeid = ANY(%(PHARMACY_SERVICE_TYPE_IDS)s) "
            "AND s.statusid = %(ACTIVE_STATUS_ID)s "
        ),
        query_vars={
            "ODS": "FQ038%",
            "PHARMACY_SERVICE_TYPE_IDS": [13, 131, 132, 134, 137],
            "ACTIVE_STATUS_ID": ACTIVE_STATUS_ID,
        },
    )
    mock_cursor.fetchall.assert_called_with()
    mock_cursor.close.assert_called_with()


@patch(f"{FILE_PATH}.connect_to_dos_db_replica")
@patch(f"{FILE_PATH}.query_dos_db")
def test_get_matching_dos_services_pharmacy_first_services_returned(mock_query_dos_db, mock_connect_to_dos_db_replica):
    # Arrange
    odscode = "FQ038"
    name = "My Pharmacy"
    service_id = 22851351399
    db_return = [get_db_item(odscode, name, id=service_id)]
    mock_connection = MagicMock()
    mock_connect_to_dos_db_replica.return_value.__enter__.return_value = mock_connection
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = db_return
    mock_query_dos_db.return_value = mock_cursor
    # Act
    response = get_matching_dos_services(odscode, True)
    # Assert
    service = response[0]
    assert service.odscode == odscode
    assert service.id == service_id
    assert service.name == name
    mock_query_dos_db.assert_called_once_with(
        connection=mock_connection,
        query=(
            "SELECT s.id, uid, s.name, odscode, address, postcode, web, typeid,"
            "statusid, ss.name status_name, publicphone, publicname, st.name service_type_name "
            "FROM services s LEFT JOIN servicetypes st ON s.typeid = st.id "
            "LEFT JOIN servicestatuses ss on s.statusid = ss.id "
            "WHERE s.odscode LIKE %(ODS)s AND s.typeid = ANY(%(PHARMACY_SERVICE_TYPE_IDS)s) "
            "AND s.statusid = %(ACTIVE_STATUS_ID)s OR s.odscode LIKE %(ODS)s AND s.typeid = "
            "ANY(%(PHARMACY_FIRST_SERVICE_TYPE_IDS)s) AND s.statusid = ANY(%(PHARMACY_FIRST_STATUSES)s)"
        ),
        query_vars={
            "ODS": "FQ038%",
            "PHARMACY_SERVICE_TYPE_IDS": [13, 131, 132, 134, 137],
            "ACTIVE_STATUS_ID": ACTIVE_STATUS_ID,
            "PHARMACY_FIRST_SERVICE_TYPE_IDS": [148, 149],
            "PHARMACY_FIRST_STATUSES": [1, 2, 3],
        },
    )
    mock_cursor.fetchall.assert_called_with()
    mock_cursor.close.assert_called_with()


def test_any_generic_bankholiday_open_periods():
    dos_service = dummy_dos_service()
    dos_service.standard_opening_times = StandardOpeningTimes()
    op1 = OpenPeriod(time(8, 0, 0), time(13, 0, 0))
    op2 = OpenPeriod(time(14, 0, 0), time(18, 0, 0))

    assert dos_service.any_generic_bankholiday_open_periods() is False

    dos_service.standard_opening_times.add_open_period(op1, "monday")
    assert dos_service.any_generic_bankholiday_open_periods() is False

    dos_service.standard_opening_times.add_open_period(op2, "monday")
    assert dos_service.any_generic_bankholiday_open_periods() is False

    dos_service.standard_opening_times.add_open_period(op1, "tuesday")
    dos_service.standard_opening_times.add_open_period(op1, "wednesday")
    dos_service.standard_opening_times.add_open_period(op1, "thursday")
    dos_service.standard_opening_times.add_open_period(op1, "friday")
    dos_service.standard_opening_times.add_open_period(op1, "saturday")
    dos_service.standard_opening_times.add_open_period(op1, "sunday")
    assert dos_service.any_generic_bankholiday_open_periods() is False

    dos_service.standard_opening_times.add_open_period(op1, "bankholiday")
    assert dos_service.any_generic_bankholiday_open_periods()

    dos_service.standard_opening_times.add_open_period(op2, "bankholiday")
    assert dos_service.any_generic_bankholiday_open_periods()

    dos_service.standard_opening_times.generic_bankholiday = []
    assert dos_service.any_generic_bankholiday_open_periods() is False


@patch(f"{FILE_PATH}.connect_to_dos_db_replica")
@patch(f"{FILE_PATH}.query_dos_db")
def test_get_matching_dos_services_no_services_returned(mock_query_dos_db, mock_connect_to_dos_db_replica):
    # Arrange
    odscode = "FQ038"
    db_return = []
    mock_connection = MagicMock()
    mock_connect_to_dos_db_replica.return_value.__enter__.return_value = mock_connection
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = db_return
    mock_query_dos_db.return_value = mock_cursor
    # Act
    response = get_matching_dos_services(odscode, False)
    # Assert
    assert response == []
    mock_query_dos_db.assert_called_once_with(
        connection=mock_connection,
        query=(
            "SELECT s.id, uid, s.name, odscode, address, postcode, web, typeid,"
            "statusid, ss.name status_name, publicphone, publicname, st.name service_type_name "
            "FROM services s LEFT JOIN servicetypes st ON s.typeid = st.id "
            "LEFT JOIN servicestatuses ss on s.statusid = ss.id "
            "WHERE s.odscode LIKE %(ODS)s AND s.typeid = ANY(%(PHARMACY_SERVICE_TYPE_IDS)s) "
            "AND s.statusid = %(ACTIVE_STATUS_ID)s "
        ),
        query_vars={
            "ODS": f"{odscode[:5]}%",
            "PHARMACY_SERVICE_TYPE_IDS": [13, 131, 132, 134, 137],
            "ACTIVE_STATUS_ID": 1,
        },
    )
    mock_cursor.fetchall.assert_called_with()
    mock_cursor.close.assert_called_with()


@patch(f"{FILE_PATH}.connect_to_dos_db_replica")
@patch(f"{FILE_PATH}.query_dos_db")
def test_get_specified_opening_times_from_db_times_returned(mock_query_dos_db, mock_connect_to_dos_db_replica):
    # Arrange
    mock_connection = MagicMock()
    mock_connect_to_dos_db_replica.return_value.__enter__.return_value = mock_connection
    mock_cursor = MagicMock()
    db_return = [
        {
            "serviceid": 28334,
            "date": date(2019, 5, 6),
            "starttime": time(8, 0, 0),
            "endtime": time(20, 0, 0),
            "isclosed": False,
        },
        {
            "serviceid": 28334,
            "date": date(2019, 5, 27),
            "starttime": time(8, 0, 0),
            "endtime": time(20, 0, 0),
            "isclosed": False,
        },
        {
            "serviceid": 28334,
            "date": date(2019, 8, 26),
            "starttime": time(8, 0, 0),
            "endtime": time(20, 0, 0),
            "isclosed": False,
        },
        {
            "serviceid": 28334,
            "date": date(2019, 8, 26),
            "starttime": time(21, 0, 0),
            "endtime": time(22, 0, 0),
            "isclosed": False,
        },
        {
            "serviceid": 28334,
            "date": date(2019, 9, 20),
            "starttime": time(0, 0, 0),
            "endtime": time(0, 0, 0),
            "isclosed": True,
        },
        {
            "serviceid": 28334,
            "date": date(2019, 9, 21),
            "starttime": time(14, 30, 0),
            "endtime": time(16, 0, 0),
            "isclosed": True,
        },
        {
            "serviceid": 28334,
            "date": date(2019, 5, 6),
            "starttime": time(6, 0, 0),
            "endtime": time(7, 0, 0),
            "isclosed": False,
        },
    ]
    mock_cursor.fetchall.return_value = db_return
    mock_query_dos_db.return_value = mock_cursor
    service_id = 123456
    expected_responses_set = sorted(
        [
            "<SpecifiedOpenTime: 06-05-2019 open=True [06:00:00-07:00:00, 08:00:00-20:00:00]>",
            "<SpecifiedOpenTime: 27-05-2019 open=True [08:00:00-20:00:00]>",
            "<SpecifiedOpenTime: 26-08-2019 open=True [08:00:00-20:00:00, 21:00:00-22:00:00]>",
            "<SpecifiedOpenTime: 20-09-2019 open=False []>",
            "<SpecifiedOpenTime: 21-09-2019 open=False []>",
        ],
    )
    # Act
    responses = get_specified_opening_times_from_db(connection=mock_connection, service_id=service_id)
    responses_str = sorted([repr(s) for s in responses])
    # Assert
    assert (
        responses_str == expected_responses_set
    ), f"Should return {expected_responses_set} string, actually: {responses_str}"

    mock_query_dos_db.assert_called_once_with(
        connection=mock_connection,
        query="SELECT ssod.serviceid, ssod.date, ssot.starttime, ssot.endtime, ssot.isclosed "
        "FROM servicespecifiedopeningdates ssod "
        "INNER JOIN servicespecifiedopeningtimes ssot "
        "ON ssod.id = ssot.servicespecifiedopeningdateid "
        "WHERE ssod.serviceid = %(SERVICE_ID)s",
        query_vars={"SERVICE_ID": service_id},
    )


@patch(f"{FILE_PATH}.connect_to_dos_db_replica")
@patch(f"{FILE_PATH}.query_dos_db")
def test_get_standard_opening_times_from_db_times_returned(mock_query_dos_db, mock_connect_to_dos_db_replica):
    # Arrange
    db_return = [
        {"serviceid": 28334, "dayid": 1, "name": "Tuesday", "starttime": time(8, 0, 0), "endtime": time(17, 0, 0)},
        {"serviceid": 28334, "dayid": 1, "name": "Friday", "starttime": time(9, 0, 0), "endtime": time(11, 30, 0)},
        {"serviceid": 28334, "dayid": 1, "name": "Friday", "starttime": time(13, 0, 0), "endtime": time(15, 30, 0)},
    ]
    mock_cursor = MagicMock()
    service_id = 123456
    mock_cursor.fetchall.return_value = db_return
    mock_query_dos_db.return_value = mock_cursor
    expected_std_opening_times = StandardOpeningTimes()
    expected_std_opening_times.add_open_period(OpenPeriod(time(8, 0, 0), time(17, 0, 0)), "tuesday")
    expected_std_opening_times.add_open_period(OpenPeriod(time(9, 0, 0), time(11, 30, 0)), "friday")
    expected_std_opening_times.add_open_period(OpenPeriod(time(13, 0, 0), time(15, 30, 0)), "friday")
    mock_connection = MagicMock()
    mock_connect_to_dos_db_replica.return_value.__enter__.return_value = mock_connection
    # Act
    response = get_standard_opening_times_from_db(connection=mock_connection, service_id=service_id)
    # Assert
    assert (
        response == expected_std_opening_times
    ), f"Should return {expected_std_opening_times} string, actually: {response}"

    mock_query_dos_db.assert_called_once_with(
        connection=mock_connection,
        query="SELECT sdo.serviceid, sdo.dayid, otd.name, sdot.starttime, sdot.endtime "
        "FROM servicedayopenings sdo "
        "INNER JOIN servicedayopeningtimes sdot "
        "ON sdo.id = sdot.servicedayopeningid "
        "LEFT JOIN openingtimedays otd "
        "ON sdo.dayid = otd.id "
        "WHERE sdo.serviceid = %(SERVICE_ID)s",
        query_vars={"SERVICE_ID": service_id},
    )


@patch(f"{FILE_PATH}.connect_to_dos_db_replica")
@patch(f"{FILE_PATH}.query_dos_db")
def test_get_specified_opening_times_from_db_no_times_returned(mock_query_dos_db, mock_connect_to_dos_db_replica):
    # Arrange
    mock_connection = MagicMock()
    mock_connect_to_dos_db_replica.return_value.__enter__.return_value = mock_connection
    mock_cursor = MagicMock()
    db_return = []
    mock_cursor.fetchall.return_value = db_return
    mock_query_dos_db.return_value = mock_cursor
    service_id = 123456
    expected_responses_set = sorted([])
    # Act
    responses = get_specified_opening_times_from_db(connection=mock_connection, service_id=service_id)
    responses_str = sorted([str(s) for s in responses])
    # Assert
    assert (
        responses_str == expected_responses_set
    ), f"Should return {expected_responses_set} string, actually: {responses_str}"

    mock_query_dos_db.assert_called_once_with(
        connection=mock_connection,
        query="SELECT ssod.serviceid, ssod.date, ssot.starttime, ssot.endtime, ssot.isclosed "
        "FROM servicespecifiedopeningdates ssod "
        "INNER JOIN servicespecifiedopeningtimes ssot "
        "ON ssod.id = ssot.servicespecifiedopeningdateid "
        "WHERE ssod.serviceid = %(SERVICE_ID)s",
        query_vars={"SERVICE_ID": service_id},
    )


@patch(f"{FILE_PATH}.connect_to_dos_db_replica")
@patch(f"{FILE_PATH}.query_dos_db")
def test_get_dos_locations(mock_query_dos_db, mock_connect_to_dos_db_replica):
    # Arrange
    mock_connection = MagicMock()
    mock_connect_to_dos_db_replica.return_value.__enter__.return_value = mock_connection
    mock_cursor = MagicMock()
    postcode = "BA2 7AF"
    db_return = [
        {
            "id": 111,
            "postcode": postcode,
            "easting": 2,
            "northing": 3,
            "postaltown": "town",
            "latitude": 4.0,
            "longitude": 2.0,
        },
    ]
    mock_cursor.fetchall.return_value = db_return
    mock_query_dos_db.return_value = mock_cursor
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

    norm_pc = postcode.replace(" ", "").upper()
    postcode_variations = [norm_pc] + [f"{norm_pc[:i]} {norm_pc[i:]}" for i in range(1, len(norm_pc))]

    mock_query_dos_db.assert_called_once_with(
        connection=mock_connection,
        query="SELECT id, postcode, easting, northing, postaltown, latitude, longitude "
        "FROM locations WHERE postcode = ANY(%(pc_variations)s)",
        query_vars={"pc_variations": postcode_variations},
    )


@patch(f"{FILE_PATH}.get_dos_locations")
def test_get_valid_dos_location(mock_get_dos_locations: MagicMock):
    # Arrange
    mock_get_dos_locations.return_value.is_valid.return_value = True
    mock_get_dos_locations.return_value = mock_location = [MagicMock()]
    postcode = "BA2 7AF"
    # Act
    location = get_valid_dos_location(postcode)
    # Assert
    assert location == mock_location[0]


@patch(f"{FILE_PATH}.get_dos_locations")
def test_get_valid_dos_location_invalid_postcode(mock_get_dos_locations: MagicMock):
    # Arrange
    mock_get_dos_locations.return_value.is_valid.return_value = False
    postcode = "BA2 7AF"
    # Act
    location = get_valid_dos_location(postcode)
    # Assert
    assert location is None


def test_db_rows_to_spec_open_times():
    db_rows = [
        {
            "serviceid": 1,
            "date": date(2019, 5, 6),
            "starttime": time(8, 0, 0),
            "endtime": time(20, 0, 0),
            "isclosed": False,
        },
        {
            "serviceid": 1,
            "date": date(2019, 5, 6),
            "starttime": time(21, 0, 0),
            "endtime": time(22, 0, 0),
            "isclosed": False,
        },
        {
            "serviceid": 1,
            "date": date(2019, 5, 27),
            "starttime": time(8, 0, 0),
            "endtime": time(20, 0, 0),
            "isclosed": False,
        },
        {
            "serviceid": 1,
            "date": date(2019, 8, 26),
            "starttime": time(8, 0, 0),
            "endtime": time(20, 0, 0),
            "isclosed": False,
        },
        {"serviceid": 1, "date": date(2019, 9, 20), "starttime": None, "endtime": None, "isclosed": True},
        {
            "serviceid": 1,
            "date": date(2020, 5, 6),
            "starttime": time(6, 0, 0),
            "endtime": time(7, 0, 0),
            "isclosed": False,
        },
    ]

    spec_open_times = db_rows_to_spec_open_times(db_rows)

    expected_spec_open_times = [
        SpecifiedOpeningTime([OP("08:00-20:00"), OP("21:00-22:00")], date(2019, 5, 6), True),
        SpecifiedOpeningTime([OP("08:00-20:00")], date(2019, 5, 27), True),
        SpecifiedOpeningTime([OP("08:00-20:00")], date(2019, 8, 26), True),
        SpecifiedOpeningTime([], date(2019, 9, 20), False),
        SpecifiedOpeningTime([OP("06:00-07:00")], date(2020, 5, 6), True),
    ]

    assert spec_open_times == expected_spec_open_times


def test_db_rows_to_spec_open_times_map():
    db_rows = [
        {"serviceid": 214, "date": date(2019, 9, 20), "starttime": None, "endtime": None, "isclosed": True},
        {
            "serviceid": 1,
            "date": date(2019, 5, 6),
            "starttime": time(8, 0, 0),
            "endtime": time(20, 0, 0),
            "isclosed": False,
        },
        {
            "serviceid": 1,
            "date": date(2019, 5, 6),
            "starttime": time(21, 0, 0),
            "endtime": time(22, 0, 0),
            "isclosed": False,
        },
        {
            "serviceid": 1,
            "date": date(2019, 5, 27),
            "starttime": time(8, 0, 0),
            "endtime": time(20, 0, 0),
            "isclosed": False,
        },
        {
            "serviceid": 214,
            "date": date(2019, 8, 26),
            "starttime": time(8, 0, 0),
            "endtime": time(20, 0, 0),
            "isclosed": False,
        },
        {
            "serviceid": 333,
            "date": date(2020, 5, 6),
            "starttime": time(6, 0, 0),
            "endtime": time(7, 0, 0),
            "isclosed": False,
        },
    ]

    spec_open_times_map = db_rows_to_spec_open_times_map(db_rows)

    expected_spec_open_times_map = {
        1: [
            SpecifiedOpeningTime([OP("08:00-20:00"), OP("21:00-22:00")], date(2019, 5, 6), True),
            SpecifiedOpeningTime([OP("08:00-20:00")], date(2019, 5, 27), True),
        ],
        214: [
            SpecifiedOpeningTime([OP("08:00-20:00")], date(2019, 8, 26), True),
            SpecifiedOpeningTime([], date(2019, 9, 20), False),
        ],
        333: [SpecifiedOpeningTime([OP("06:00-07:00")], date(2020, 5, 6), True)],
    }

    assert spec_open_times_map == expected_spec_open_times_map


def test_db_rows_to_std_open_time():
    db_rows = [
        {"serviceid": 1, "dayid": 0, "name": "Monday", "starttime": time(8, 0, 0), "endtime": time(17, 0, 0)},
        {"serviceid": 1, "dayid": 6, "name": "Sunday", "starttime": time(13, 0, 0), "endtime": time(15, 30, 0)},
        {"serviceid": 1, "dayid": 1, "name": "Tuesday", "starttime": time(13, 0, 0), "endtime": time(18, 0, 0)},
        {"serviceid": 1, "dayid": 4, "name": "Friday", "starttime": time(13, 0, 0), "endtime": time(15, 30, 0)},
        {"serviceid": 1, "dayid": 6, "name": "Wednesday", "starttime": time(7, 0, 0), "endtime": time(15, 30, 0)},
        {"serviceid": 1, "dayid": 1, "name": "Tuesday", "starttime": time(8, 0, 0), "endtime": time(12, 0, 0)},
        {"serviceid": 1, "dayid": 4, "name": "Thursday", "starttime": time(11, 0, 0), "endtime": time(13, 30, 0)},
    ]

    expcted_std_open_times = StandardOpeningTimes()
    expcted_std_open_times.monday = [OP("08:00-17:00")]
    expcted_std_open_times.tuesday = [OP("08:00-12:00"), OP("13:00-18:00")]
    expcted_std_open_times.wednesday = [OP("07:00-15:30")]
    expcted_std_open_times.thursday = [OP("11:00-13:30")]
    expcted_std_open_times.friday = [OP("13:00-15:30")]
    expcted_std_open_times.sunday = [OP("13:00-15:30")]

    actual_std_open_times = db_rows_to_std_open_times(db_rows)

    assert actual_std_open_times == expcted_std_open_times


def test_db_rows_to_std_open_times_map():
    db_rows = [
        {"serviceid": 22, "dayid": 4, "name": "Friday", "starttime": time(13, 0, 0), "endtime": time(15, 30, 0)},
        {"serviceid": 22, "dayid": 6, "name": "Wednesday", "starttime": time(7, 0, 0), "endtime": time(15, 30, 0)},
        {"serviceid": 22, "dayid": 1, "name": "Tuesday", "starttime": time(8, 0, 0), "endtime": time(12, 0, 0)},
        {"serviceid": 22, "dayid": 4, "name": "Thursday", "starttime": time(11, 0, 0), "endtime": time(13, 30, 0)},
        {"serviceid": 1, "dayid": 0, "name": "Monday", "starttime": time(8, 0, 0), "endtime": time(17, 0, 0)},
        {"serviceid": 1, "dayid": 6, "name": "Sunday", "starttime": time(13, 0, 0), "endtime": time(15, 30, 0)},
        {"serviceid": 1, "dayid": 1, "name": "Tuesday", "starttime": time(8, 0, 0), "endtime": time(12, 0, 0)},
        {"serviceid": 1, "dayid": 4, "name": "Thursday", "starttime": time(11, 0, 0), "endtime": time(13, 30, 0)},
        {"serviceid": 333, "dayid": 0, "name": "Monday", "starttime": time(10, 0, 0), "endtime": time(17, 0, 0)},
        {"serviceid": 333, "dayid": 6, "name": "Sunday", "starttime": time(13, 0, 0), "endtime": time(15, 30, 0)},
        {"serviceid": 22, "dayid": 0, "name": "Monday", "starttime": time(13, 0, 0), "endtime": time(17, 0, 0)},
        {"serviceid": 22, "dayid": 6, "name": "Sunday", "starttime": time(13, 0, 0), "endtime": time(15, 30, 0)},
        {"serviceid": 22, "dayid": 1, "name": "Tuesday", "starttime": time(13, 0, 0), "endtime": time(18, 0, 0)},
        {"serviceid": 333, "dayid": 1, "name": "Tuesday", "starttime": time(13, 0, 0), "endtime": time(18, 0, 0)},
        {"serviceid": 333, "dayid": 4, "name": "Friday", "starttime": time(13, 0, 0), "endtime": time(15, 30, 0)},
        {"serviceid": 333, "dayid": 6, "name": "Wednesday", "starttime": time(7, 0, 0), "endtime": time(15, 30, 0)},
        {"serviceid": 333, "dayid": 1, "name": "Tuesday", "starttime": time(8, 0, 0), "endtime": time(12, 0, 0)},
        {"serviceid": 333, "dayid": 4, "name": "Thursday", "starttime": time(11, 0, 0), "endtime": time(13, 30, 0)},
        {"serviceid": 1, "dayid": 1, "name": "Tuesday", "starttime": time(13, 0, 0), "endtime": time(18, 0, 0)},
        {"serviceid": 1, "dayid": 4, "name": "Friday", "starttime": time(13, 0, 0), "endtime": time(15, 30, 0)},
        {"serviceid": 1, "dayid": 6, "name": "Wednesday", "starttime": time(7, 0, 0), "endtime": time(15, 30, 0)},
    ]

    expcted_std_open_times_1 = StandardOpeningTimes()
    expcted_std_open_times_1.monday = [OP("08:00-17:00")]
    expcted_std_open_times_1.tuesday = [OP("08:00-12:00"), OP("13:00-18:00")]
    expcted_std_open_times_1.wednesday = [OP("07:00-15:30")]
    expcted_std_open_times_1.thursday = [OP("11:00-13:30")]
    expcted_std_open_times_1.friday = [OP("13:00-15:30")]
    expcted_std_open_times_1.sunday = [OP("13:00-15:30")]

    expcted_std_open_times_22 = StandardOpeningTimes()
    expcted_std_open_times_22.monday = [OP("13:00-17:00")]
    expcted_std_open_times_22.tuesday = [OP("08:00-12:00"), OP("13:00-18:00")]
    expcted_std_open_times_22.wednesday = [OP("07:00-15:30")]
    expcted_std_open_times_22.thursday = [OP("11:00-13:30")]
    expcted_std_open_times_22.friday = [OP("13:00-15:30")]
    expcted_std_open_times_22.sunday = [OP("13:00-15:30")]

    expcted_std_open_times_333 = StandardOpeningTimes()
    expcted_std_open_times_333.monday = [OP("10:00-17:00")]
    expcted_std_open_times_333.tuesday = [OP("08:00-12:00"), OP("13:00-18:00")]
    expcted_std_open_times_333.wednesday = [OP("07:00-15:30")]
    expcted_std_open_times_333.thursday = [OP("11:00-13:30")]
    expcted_std_open_times_333.friday = [OP("13:00-15:30")]
    expcted_std_open_times_333.sunday = [OP("13:00-15:30")]

    expcted_std_open_times_map = {
        1: expcted_std_open_times_1,
        22: expcted_std_open_times_22,
        333: expcted_std_open_times_333,
    }

    actual_std_open_times_map = db_rows_to_std_open_times_map(db_rows)

    assert actual_std_open_times_map == expcted_std_open_times_map


def get_db_item(odscode="FA9321", name="fake name", id=9999, typeid=13):  # noqa: A002
    return {
        "id": id,
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
        "typeid": typeid,
        "parentid": 123486,
        "subregionid": 21813557,
        "statusid": 1,
        "createdtime": datetime(2011, 8, 24, 9, 17, 24, tzinfo=timezone.utc),
        "modifiedtime": datetime(2019, 3, 13, 0, 37, 7, tzinfo=timezone.utc),
        "publicphone": "0123 012 012",
        "publicname": None,
        "service_type_name": "my service",
    }


@patch(f"{FILE_PATH}.query_dos_db")
def test_has_palliative_care(mock_query_dos_db: MagicMock):
    # Arrange
    dos_service = dummy_dos_service()
    dos_service.typeid = 13
    connection = MagicMock()
    expected_sql_command = """SELECT sgsds.id as z_code from servicesgsds sgsds
            WHERE sgsds.serviceid = %(SERVICE_ID)s
            AND sgsds.sgid = %(PALIATIVE_CARE_SYMPTOM_GROUP)s
            AND sgsds.sdid  = %(PALIATIVE_CARE_SYMPTOM_DESCRIMINATOR)s
            """
    expected_named_args = {
        "SERVICE_ID": dos_service.id,
        "PALIATIVE_CARE_SYMPTOM_GROUP": DOS_PALLIATIVE_CARE_SYMPTOM_GROUP,
        "PALIATIVE_CARE_SYMPTOM_DESCRIMINATOR": DOS_PALLIATIVE_CARE_SYMPTOM_DISCRIMINATOR,
    }
    # Act
    assert True is has_palliative_care(dos_service, connection)
    # Assert
    mock_query_dos_db.assert_called_once_with(
        connection=connection,
        query=expected_sql_command,
        query_vars=expected_named_args,
    )


@patch(f"{FILE_PATH}.query_dos_db")
def test_has_palliative_care_not_correct_type(mock_query_dos_db: MagicMock):
    # Arrange
    dos_service = dummy_dos_service()
    dos_service.typeid = 0
    connection = MagicMock()
    # Act
    assert False is has_palliative_care(dos_service, connection)
    # Assert
    mock_query_dos_db.assert_not_called()


@patch(f"{FILE_PATH}.query_dos_db")
@patch(f"{FILE_PATH}.connect_to_dos_db_replica")
def test_get_region(mock_connect_to_dos_db_replica: MagicMock, mock_query_dos_db: MagicMock) -> None:
    # Arrange
    mock_connect_to_dos_db_replica.return_value = mock_connection = MagicMock()
    mock_query_dos_db.return_value.fetchone.return_value = {"region": "South East"}
    service_id = 123
    # Act
    region = get_region(service_id)
    # Assert
    assert region == "South East"
    mock_connect_to_dos_db_replica.assert_called_once()
    mock_query_dos_db.assert_called_once_with(
        connection=mock_connection.__enter__.return_value,
        query="""WITH
RECURSIVE servicetree as
(SELECT ser.parentid, ser.id, ser.uid, ser.name, 1 AS lvl
FROM services ser where ser.id = %(SERVICE_ID)s
UNION ALL
SELECT ser.parentid, st.id, ser.uid, ser.name, lvl+1 AS lvl
FROM services ser
INNER JOIN servicetree st ON ser.id = st.parentid),
serviceregion as
(SELECT st.*, ROW_NUMBER() OVER (PARTITION BY st.id ORDER BY st.lvl desc) rn
FROM servicetree st)
SELECT sr.name region
FROM serviceregion sr
INNER JOIN services ser ON sr.id = ser.id
LEFT OUTER JOIN services par ON ser.parentid = par.id
WHERE sr.rn=1
ORDER BY ser.name
    """,
        query_vars={"SERVICE_ID": service_id},
    )
