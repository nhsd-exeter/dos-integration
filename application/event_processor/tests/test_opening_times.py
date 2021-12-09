import pytest
from datetime import datetime, date, time, timedelta

from ..opening_times import OpenPeriod, SpecifiedOpeningTime, StandardOpeningTimes, any_overlaps


@pytest.mark.parametrize("start, end, other_start,other_end, expected", [
    (time(8, 0), time(12, 0), time(8, 0), time(12, 0), True),
    (time(8, 0), time(12, 0), time(13, 0), time(23, 0), False)])
def test_openperiod_eq(start, end, other_start, other_end, expected):
    # Arrange
    open_period = OpenPeriod(start, end)
    # Act
    actual = open_period.__eq__(OpenPeriod(other_start, other_end))
    # Assert
    assert expected == actual, f"Should return {expected} , actually: {actual}"


@pytest.mark.parametrize("start, end, expected", [
    (time(8, 0), time(12, 0), True),
    (time(12, 0), time(8, 0), False)])
def test_openperiod_start_before_end(start, end, expected):
    # Arrange
    open_period = OpenPeriod(start, end)
    # Act
    actual = open_period.start_before_end()
    # Assert
    assert expected == actual, f"Should return {expected} , actually: {actual}"


@pytest.mark.parametrize("start, end, other_start,other_end, expected", [
    (time(8, 0), time(12, 0), time(8, 0), time(11, 0), True),
    (time(8, 0), time(12, 0), time(13, 0), time(23, 0), False)])
def test_openperiod_overlaps(start, end, other_start, other_end, expected):
    # Arrange
    open_period = OpenPeriod(start, end)
    # Act
    actual = open_period.overlaps(OpenPeriod(other_start, other_end))
    # Assert
    assert expected == actual, f"Should return {expected} , actually: {actual}"


def test_openperiod_str():
    assert str(OpenPeriod(time(8, 0, 0), time(15, 0, 0))) == "08:00:00-15:00:00"
    assert str(OpenPeriod(time(0, 0, 0), time(15, 0, 0))) == "00:00:00-15:00:00"
    assert str(OpenPeriod(time(8, 0, 0), time(23, 59, 59))) == "08:00:00-23:59:59"
    assert str(OpenPeriod(time(0, 0, 0), time(23, 59, 59))) == "00:00:00-23:59:59"
    assert str(OpenPeriod(time(1, 2, 3), time(4, 5, 6))) == "01:02:03-04:05:06"
    assert str(OpenPeriod(time(13, 35, 23), time(13, 35, 24))) == "13:35:23-13:35:24"


def test_openperiod_export_cr_format():
    assert (
        OpenPeriod(time(8, 0, 0), time(15, 0, 0)).export_cr_format() ==
        {
            "start_time": "08:00",
            "end_time": "15:00"
        }
    )
    assert (
        OpenPeriod(time(0, 0, 0), time(15, 0, 0)).export_cr_format() ==
        {
            "start_time": "00:00",
            "end_time": "15:00"
        }
    )
    assert (
        OpenPeriod(time(8, 0, 0), time(23, 59, 0)).export_cr_format() ==
        {
            "start_time": "08:00",
            "end_time": "23:59"
        }
    )
    assert (
        OpenPeriod(time(8, 0, 0), time(23, 59, 59)).export_cr_format() ==
        {
            "start_time": "08:00",
            "end_time": "23:59"
        }
    )
    assert (
        OpenPeriod(time(0, 0, 0), time(23, 59, 59)).export_cr_format() ==
        {
            "start_time": "00:00",
            "end_time": "23:59"
        }
    )
    assert (
        OpenPeriod(time(1, 2, 3), time(4, 5, 0)).export_cr_format() ==
        {
            "start_time": "01:02",
            "end_time": "04:05"
        }
    )
    assert (
        OpenPeriod(time(13, 35, 0), time(13, 36, 0)).export_cr_format() ==
        {
            "start_time": "13:35",
            "end_time": "13:36"
        }
    )


def test_open_period__lt__gt__():

    a = OpenPeriod(time(8, 0, 0), time(12, 0, 0))
    b = OpenPeriod(time(9, 0, 0), time(12, 0, 0))
    assert a < b
    assert b > a

    a = OpenPeriod(time(8, 0, 0), time(12, 0, 0))
    b = OpenPeriod(time(8, 0, 1), time(12, 0, 0))
    assert a < b
    assert b > a

    a = OpenPeriod(time(8, 0, 0), time(12, 0, 0))
    b = OpenPeriod(time(8, 0, 0), time(12, 0, 1))
    assert a < b
    assert b > a

    a = OpenPeriod(time(8, 0, 0), time(12, 0, 0))
    b = OpenPeriod(time(8, 0, 0), time(13, 0, 0))
    assert a < b
    assert b > a

    a = OpenPeriod(time(8, 0, 0), time(12, 0, 0))
    b = OpenPeriod(time(8, 0, 0), time(12, 0, 0))
    assert not a < b
    assert not a > b
    assert not b < a
    assert not b > a


def test_open_period_hash():
    open_period = OpenPeriod(time(8, 0, 0), time(12, 0, 0))
    equal_ops = (
        OpenPeriod(time(8, 0, 0), time(12, 0, 0)),
        OpenPeriod(time(8, 0, 0), time(12, 0, 0)),
        OpenPeriod(datetime(1970, 1, 1, 8, 0, 0).time(), time(12, 0, 0)),
        OpenPeriod(datetime.strptime("8:00", "%H:%M").time(), time(12, 0, 0)),
        OpenPeriod(time(8, 0, 0), datetime.strptime("12:00:00", "%H:%M:%S").time()),
        OpenPeriod(
            datetime.strptime("8:00", "%H:%M").time(),
            datetime.strptime("12:00:00", "%H:%M:%S").time()),
        OpenPeriod(
            (datetime(2000, 1, 1, 7, 0, 0) + timedelta(hours=1)).time(),
            time(12, 0, 0))
    )

    for op in equal_ops:
        assert open_period == op,\
                f"{open_period} not found to be equal to {op}"
        assert hash(open_period) == hash(op),\
            f"hash {hash(open_period)} not found to be equal to {hash(op)}"


@pytest.mark.parametrize("open_periods, date, other_open_periods,other_date, expected", [
    (
        [OpenPeriod(time(8, 0), time(12, 0)), OpenPeriod(time(13, 0), time(21, 0))],
        date(2019, 5, 21),
        [OpenPeriod(time(8, 0), time(12, 0)), OpenPeriod(time(13, 0), time(21, 0))],
        date(2019, 5, 23),
        False),
    (
        [OpenPeriod(time(8, 0), time(12, 0)), OpenPeriod(time(13, 0), time(21, 0))],
        date(2019, 5, 23),
        [OpenPeriod(time(8, 0), time(12, 0)), OpenPeriod(time(13, 0), time(21, 0))],
        date(2019, 5, 23),
        True)])
def test_specifiedopeningtime_eq(open_periods, date, other_open_periods, other_date, expected):
    # Arrange
    specified_open_period = SpecifiedOpeningTime(open_periods, date)
    # Act
    actual = specified_open_period.__eq__(SpecifiedOpeningTime(other_open_periods, other_date))
    # Assert
    assert expected == actual, f"Should return {expected} , actually: {actual}"


@pytest.mark.parametrize("expected, actual", [
    (
        {"2021-12-25": []}, SpecifiedOpeningTime([], date(2021, 12, 25))
    ),
    (
        {
            "2021-03-02":
                [
                    {
                        "start_time": "08:00",
                        "end_time": "17:00"
                    }
                ]
        },
        SpecifiedOpeningTime([OpenPeriod(time(8, 0, 0), time(17, 0, 0))], date(2021, 3, 2))
    ),
    (
        {
            "2039-12-30":
                [
                    {
                        "start_time": "02:00",
                        "end_time": "09:30"
                    },
                    {
                        "start_time": "11:45",
                        "end_time": "18:00"
                    }
                ]
        },
        SpecifiedOpeningTime(
            [
                OpenPeriod(time(2, 0, 0), time(9, 30, 0)),
                OpenPeriod(time(11, 45, 0), time(18, 0, 0))
            ],
            date(2039, 12, 30))
    ),
    (
        {
            "2060-06-01":
                [
                    {
                        "start_time": "05:00",
                        "end_time": "09:30"
                    },
                    {
                        "start_time": "11:45",
                        "end_time": "18:00"
                    },
                    {
                        "start_time": "20:45",
                        "end_time": "22:00"
                    }
                ]
        },
        SpecifiedOpeningTime(
            [
                OpenPeriod(time(5, 0, 0), time(9, 30, 0)),
                OpenPeriod(time(20, 45, 0), time(22, 0, 0)),
                OpenPeriod(time(11, 45, 0), time(18, 0, 0))
            ],
            date(2060, 6, 1))
    )
    ])
def test_specifiedopeningtime_export_cr_format(expected: dict, actual: SpecifiedOpeningTime):
    assert actual.export_cr_format() == expected,\
        f"expected {expected} SpecifiedOpeningTime change req format but got {actual}"


def test_standardopeningtimes_export_cr_format():

    # Start with empty
    std_opening_times = StandardOpeningTimes()
    expected = {
                    "Monday": [], "Tuesday": [], "Wednesday": [], "Thursday": [],
                    "Friday": [], "Saturday": [], "Sunday": []
                }
    assert std_opening_times.export_cr_format() == expected

    # Add single opening time for monday
    std_opening_times.monday.append(OpenPeriod(time(8, 0, 0), time(15, 0, 0)))
    expected["Monday"].append(
        {
            "start_time": "08:00",
            "end_time": "15:00"
        })
    assert std_opening_times.export_cr_format() == expected

    # Add another to tuesday
    std_opening_times.tuesday.append(OpenPeriod(time(8, 0, 0), time(20, 0, 0)))
    expected["Tuesday"].append(
        {
            "start_time": "08:00",
            "end_time": "20:00"
        })
    assert std_opening_times.export_cr_format() == expected

    # Add another to monday
    std_opening_times.monday.append(OpenPeriod(time(16, 0, 0), time(20, 0, 0)))
    expected["Monday"].append(
        {
            "start_time": "16:00",
            "end_time": "20:00"
        })
    assert std_opening_times.export_cr_format() == expected

    # Add to every other day
    for day in ["Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        getattr(std_opening_times, day.lower()).append(OpenPeriod(time(16, 0, 0), time(20, 0, 0)))
        expected[day].append(
                {
                    "start_time": "16:00",
                    "end_time": "20:00"
                }
            )
    assert std_opening_times.export_cr_format() == expected


def test_any_overlaps():

    open_periods = [
        OpenPeriod(time(1, 0, 0), time(2, 0, 0)),
        OpenPeriod(time(3, 0, 0), time(5, 0, 0)),
        OpenPeriod(time(8, 0, 0), time(12, 0, 0))
    ]
    assert any_overlaps(open_periods) is False

    open_periods.append(OpenPeriod(time(7, 0, 0), time(12, 0, 0)))
    assert any_overlaps(open_periods)
