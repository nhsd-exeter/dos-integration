import pytest
from datetime import datetime, date, time, timedelta

from ..opening_times import OpenPeriod, SpecifiedOpeningTime, StandardOpeningTimes


@pytest.mark.parametrize(
    "start, end, other_start, other_end, expected",
    [
        (time(8, 0), time(12, 0), time(8, 0), time(12, 0), True),
        (time(8, 0), time(12, 0), time(13, 0), time(23, 0), False),
    ],
)
def test_open_period_eq(start, end, other_start, other_end, expected):
    # Arrange
    open_period = OpenPeriod(start, end)
    # Act
    actual = open_period.__eq__(OpenPeriod(other_start, other_end))
    # Assert
    assert expected == actual, f"Should return {expected} , actually: {actual}"


@pytest.mark.parametrize("start, end, expected", [(time(8, 0), time(12, 0), True), (time(12, 0), time(8, 0), False)])
def test_open_period_start_before_end(start, end, expected):
    # Arrange
    open_period = OpenPeriod(start, end)
    # Act
    actual = open_period.start_before_end()
    # Assert
    assert expected == actual, f"Should return {expected} , actually: {actual}"


def test_openperiod_any_overlaps():
    open_periods = [
        OpenPeriod(time(1, 0, 0), time(2, 0, 0)),
        OpenPeriod(time(3, 0, 0), time(5, 0, 0)),
        OpenPeriod(time(8, 0, 0), time(12, 0, 0)),
    ]
    std = StandardOpeningTimes()
    std.monday = open_periods
    spec = SpecifiedOpeningTime(open_periods, date(2022, 12, 26))

    assert OpenPeriod.any_overlaps(open_periods) is False
    assert std.any_overlaps() is False
    assert spec.any_overlaps() is False

    new_op = OpenPeriod(time(7, 0, 0), time(12, 0, 0))
    open_periods.append(new_op)

    assert OpenPeriod.any_overlaps(open_periods)
    assert std.any_overlaps()
    assert spec.any_overlaps()


def test_openperiod_all_start_before_end():
    open_periods = [
        OpenPeriod(time(1, 0, 0), time(2, 0, 0)),
        OpenPeriod(time(3, 0, 0), time(5, 0, 0)),
        OpenPeriod(time(8, 0, 0), time(12, 0, 0)),
    ]
    std = StandardOpeningTimes()
    std.wednesday = open_periods
    spec = SpecifiedOpeningTime(open_periods, date(2022, 12, 24))

    assert OpenPeriod.all_start_before_end(open_periods)
    assert std.all_start_before_end()
    assert spec.all_start_before_end()

    new_op = OpenPeriod(time(9, 0, 0), time(8, 59, 0))
    open_periods.append(new_op)

    assert OpenPeriod.all_start_before_end(open_periods) is False
    assert std.all_start_before_end() is False
    assert spec.all_start_before_end() is False


def test_open_period_str():
    assert str(OpenPeriod(time(8, 0, 0), time(15, 0, 0))) == "08:00:00-15:00:00"
    assert str(OpenPeriod(time(0, 0, 0), time(15, 0, 0))) == "00:00:00-15:00:00"
    assert str(OpenPeriod(time(8, 0, 0), time(23, 59, 59))) == "08:00:00-23:59:59"
    assert str(OpenPeriod(time(0, 0, 0), time(23, 59, 59))) == "00:00:00-23:59:59"
    assert str(OpenPeriod(time(1, 2, 3), time(4, 5, 6))) == "01:02:03-04:05:06"
    assert str(OpenPeriod(time(13, 35, 23), time(13, 35, 24))) == "13:35:23-13:35:24"


def test_open_period_export_cr_format():
    assert OpenPeriod(time(8, 0, 0), time(15, 0, 0)).export_cr_format() == {"start_time": "08:00", "end_time": "15:00"}
    assert OpenPeriod(time(0, 0, 0), time(15, 0, 0)).export_cr_format() == {"start_time": "00:00", "end_time": "15:00"}
    assert OpenPeriod(time(8, 0, 0), time(23, 59, 0)).export_cr_format() == {"start_time": "08:00", "end_time": "23:59"}
    assert OpenPeriod(time(8, 0, 0), time(23, 59, 59)).export_cr_format() == {
        "start_time": "08:00",
        "end_time": "23:59",
    }
    assert OpenPeriod(time(0, 0, 0), time(23, 59, 59)).export_cr_format() == {
        "start_time": "00:00",
        "end_time": "23:59",
    }
    assert OpenPeriod(time(1, 2, 3), time(4, 5, 0)).export_cr_format() == {"start_time": "01:02", "end_time": "04:05"}
    assert OpenPeriod(time(13, 35, 0), time(13, 36, 0)).export_cr_format() == {
        "start_time": "13:35",
        "end_time": "13:36",
    }

def test_openperiod_list_string():
    a = OpenPeriod(time(8, 0, 0), time(12, 0, 0))
    b = OpenPeriod(time(13, 0, 0), time(17, 30, 0))
    c = OpenPeriod(time(19, 0, 0), time(23, 59, 59))

    assert OpenPeriod.list_string([a]) == "[08:00:00-12:00:00]"
    assert OpenPeriod.list_string([a, b]) == "[08:00:00-12:00:00, 13:00:00-17:30:00]"
    assert OpenPeriod.list_string([a, b, c]) == "[08:00:00-12:00:00, 13:00:00-17:30:00, 19:00:00-23:59:59]"
    assert OpenPeriod.list_string([b, a, c]) == "[08:00:00-12:00:00, 13:00:00-17:30:00, 19:00:00-23:59:59]"
    assert OpenPeriod.list_string([c, b, a]) == "[08:00:00-12:00:00, 13:00:00-17:30:00, 19:00:00-23:59:59]"


def test_openperiod_equal_lists():
    a = OpenPeriod(time(8, 0, 0), time(12, 0, 0))
    b = OpenPeriod(time(13, 0, 0), time(17, 30, 0))
    c = OpenPeriod(time(19, 0, 0), time(23, 59, 59))

    assert OpenPeriod.equal_lists([a], [a])
    assert OpenPeriod.equal_lists([a, b], [a, b])
    assert OpenPeriod.equal_lists([a, c], [a, c])
    assert OpenPeriod.equal_lists([b, c], [c, b])
    assert OpenPeriod.equal_lists([a, b, c], [a, b, c])
    assert OpenPeriod.equal_lists([a, b, c], [c, b, a])
    assert OpenPeriod.equal_lists([a, c, c], [c, a, c])


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


@pytest.mark.parametrize(
    "opening_period_2",
    [
        OpenPeriod(time(8, 0, 0), time(12, 0, 0)),
        OpenPeriod(time(8, 0, 0), time(12, 0, 0)),
        OpenPeriod(datetime(1970, 1, 1, 8, 0, 0).time(), time(12, 0, 0)),
        OpenPeriod(datetime.strptime("8:00", "%H:%M").time(), time(12, 0, 0)),
        OpenPeriod(time(8, 0, 0), datetime.strptime("12:00:00", "%H:%M:%S").time()),
        OpenPeriod(datetime.strptime("8:00", "%H:%M").time(), datetime.strptime("12:00:00", "%H:%M:%S").time()),
        OpenPeriod((datetime(2000, 1, 1, 7, 0, 0) + timedelta(hours=1)).time(), time(12, 0, 0)),
    ],
)
def test_open_period_hash(opening_period_2: OpenPeriod):
    open_period_1 = OpenPeriod(time(8, 0, 0), time(12, 0, 0))

    assert open_period_1 == opening_period_2, f"{open_period_1} not found to be equal to {opening_period_2}"
    assert hash(open_period_1) == hash(
        opening_period_2
    ), f"hash {hash(open_period_1)} not found to be equal to {hash(opening_period_2)}"


@pytest.mark.parametrize(
    "open_periods, date, other_open_periods,other_date, expected",
    [
        (
            [OpenPeriod(time(8, 0), time(12, 0)), OpenPeriod(time(13, 0), time(21, 0))],
            date(2019, 5, 21),
            [OpenPeriod(time(8, 0), time(12, 0)), OpenPeriod(time(13, 0), time(21, 0))],
            date(2019, 5, 23),
            False,
        ),
        (
            [OpenPeriod(time(8, 0), time(12, 0)), OpenPeriod(time(13, 0), time(21, 0))],
            date(2019, 5, 23),
            [OpenPeriod(time(8, 0), time(12, 0)), OpenPeriod(time(13, 0), time(21, 0))],
            date(2019, 5, 23),
            True,
        ),
    ],
)
def test_specifiedopeningtime_eq(open_periods, date, other_open_periods, other_date, expected):
    # Arrange
    specified_open_period = SpecifiedOpeningTime(open_periods, date)
    # Act
    actual = specified_open_period.__eq__(SpecifiedOpeningTime(other_open_periods, other_date))
    # Assert
    assert expected == actual, f"Should return {expected} , actually: {actual}"


@pytest.mark.parametrize(
    "expected, actual",
    [
        ({"2021-12-25": []}, SpecifiedOpeningTime([], date(2021, 12, 25))),
        (
            {"2021-03-02": [{"start_time": "08:00", "end_time": "17:00"}]},
            SpecifiedOpeningTime([OpenPeriod(time(8, 0, 0), time(17, 0, 0))], date(2021, 3, 2)),
        ),
        (
            {
                "2039-12-30": [
                    {"start_time": "02:00", "end_time": "09:30"},
                    {"start_time": "11:45", "end_time": "18:00"},
                ]
            },
            SpecifiedOpeningTime(
                [OpenPeriod(time(2, 0, 0), time(9, 30, 0)), OpenPeriod(time(11, 45, 0), time(18, 0, 0))],
                date(2039, 12, 30),
            ),
        ),
        (
            {
                "2060-06-01": [
                    {"start_time": "05:00", "end_time": "09:30"},
                    {"start_time": "11:45", "end_time": "18:00"},
                    {"start_time": "20:45", "end_time": "22:00"},
                ]
            },
            SpecifiedOpeningTime(
                [
                    OpenPeriod(time(5, 0, 0), time(9, 30, 0)),
                    OpenPeriod(time(20, 45, 0), time(22, 0, 0)),
                    OpenPeriod(time(11, 45, 0), time(18, 0, 0)),
                ],
                date(2060, 6, 1),
            ),
        ),
    ],
)
def test_specified_opening_time_export_cr_format(expected: dict, actual: SpecifiedOpeningTime):
    cr_format = actual.export_cr_format()
    assert (
        cr_format == expected
    ), f"expected {expected} SpecifiedOpeningTime change req format but got {cr_format}"


def test_specifiedopentime_contradiction():
    spec = SpecifiedOpeningTime([], date(2021, 12, 24), is_open=False)
    op = OpenPeriod(time(8, 0, 0), time(17, 0, 0))

    assert spec.contradiction() is False

    spec.is_open = True
    assert spec.contradiction()

    spec.open_periods.append(op)
    assert spec.contradiction() is False

    spec.is_open = False
    assert spec.contradiction()


def test_specifiedopentimes_is_valid():
    a = OpenPeriod(time(8, 0, 0), time(12, 0, 0))
    b = OpenPeriod(time(13, 0, 0), time(17, 30, 0))
    c = OpenPeriod(time(19, 0, 0), time(23, 59, 59))
    d = OpenPeriod(time(9, 0, 0), time(18, 30, 0))      # Overlaps
    e = OpenPeriod(time(9, 0, 0), time(2, 30, 0))       # Start not before end
    
    sp1 = SpecifiedOpeningTime([], date(2022, 12, 24), is_open=False)
    assert sp1.is_valid()

    sp1.is_open = True
    assert sp1.is_valid() is False

    sp1.open_periods.append(a)
    assert sp1.is_valid()

    sp1.is_open = False
    assert sp1.is_valid() is False

    sp1.open_periods.append(b)
    sp1.open_periods.append(c)
    assert sp1.is_valid() is False

    sp1.is_open = True
    assert sp1.is_valid()

    sp1.open_periods.pop(0)
    sp1.open_periods.insert(0, d)
    assert sp1.is_valid() is False

    sp1.is_open = False
    assert sp1.is_valid() is False

    sp1.open_periods.pop(0)
    assert sp1.is_valid() is False

    sp1.is_open = True
    assert sp1.is_valid()

    sp1.open_periods.insert(0, e)
    assert sp1.is_valid() is False

    sp1.is_open = False
    assert sp1.is_valid() is False


def test_specifiedopentimes_equal_lists():
    a = OpenPeriod(time(8, 0, 0), time(12, 0, 0))
    b = OpenPeriod(time(13, 0, 0), time(17, 30, 0))
    c = OpenPeriod(time(19, 0, 0), time(23, 30, 0))
    sp1 = SpecifiedOpeningTime([], date(2021, 12, 24), is_open=False)
    sp2 = SpecifiedOpeningTime([a, b, c], date(2021, 12, 24))
    sp2b = SpecifiedOpeningTime([a, b, c], date(2021, 12, 24))
    sp3 = SpecifiedOpeningTime([b], date(2021, 12, 24))

    assert sp2 == sp2b
    assert SpecifiedOpeningTime.equal_lists([sp1], [sp1])
    assert SpecifiedOpeningTime.equal_lists([sp1, sp2], [sp1, sp2])
    assert SpecifiedOpeningTime.equal_lists([sp1, sp2, sp3], [sp1, sp2, sp3])
    assert SpecifiedOpeningTime.equal_lists([sp1, sp2, sp3], [sp2, sp3, sp1])
    assert SpecifiedOpeningTime.equal_lists([sp1, sp2], [sp2, sp1])
    assert SpecifiedOpeningTime.equal_lists([sp1, sp2, sp3], [sp2b, sp3, sp1])
    assert SpecifiedOpeningTime.equal_lists([sp2], [sp2b])



def test_standard_opening_times_export_cr_format():

    # Start with empty
    std_opening_times = StandardOpeningTimes()
    expected = {
        "Monday": [],
        "Tuesday": [],
        "Wednesday": [],
        "Thursday": [],
        "Friday": [],
        "Saturday": [],
        "Sunday": [],
    }
    assert std_opening_times.export_cr_format() == expected

    # Add single opening time for monday
    std_opening_times.monday.append(OpenPeriod(time(8, 0, 0), time(15, 0, 0)))
    expected["Monday"].append({"start_time": "08:00", "end_time": "15:00"})
    assert std_opening_times.export_cr_format() == expected

    # Add another to tuesday
    std_opening_times.tuesday.append(OpenPeriod(time(8, 0, 0), time(20, 0, 0)))
    expected["Tuesday"].append({"start_time": "08:00", "end_time": "20:00"})
    assert std_opening_times.export_cr_format() == expected

    # Add another to monday
    std_opening_times.monday.append(OpenPeriod(time(16, 0, 0), time(20, 0, 0)))
    expected["Monday"].append({"start_time": "16:00", "end_time": "20:00"})
    assert std_opening_times.export_cr_format() == expected

    # Add to every other day
    for day in ["Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        getattr(std_opening_times, day.lower()).append(OpenPeriod(time(16, 0, 0), time(20, 0, 0)))
        expected[day].append({"start_time": "16:00", "end_time": "20:00"})
    assert std_opening_times.export_cr_format() == expected


def test_stdopeningtimes_eq():
    a = OpenPeriod(time(8, 0, 0), time(12, 0, 0))
    b = OpenPeriod(time(13, 0, 0), time(17, 30, 0))
    c = OpenPeriod(time(19, 0, 0), time(23, 59, 59))
    st1 = StandardOpeningTimes()
    st2 = StandardOpeningTimes()

    assert st1 == st2

    st1.monday.append(a)
    assert st1 != st2

    st2.monday.append(a)
    assert st1 == st2

    st2.friday += [a, b, c]
    st1.friday += [a, b]
    assert st1 != st2

    st1.friday.append(c)
    assert st1 == st2

    st1.sunday += [b, a, c]
    st2.sunday += [c, b, a]
    assert st1 == st2


def test_stdopeningtimes_any_contradiction():
    a = OpenPeriod(time(8, 0, 0), time(12, 0, 0))
    b = OpenPeriod(time(13, 0, 0), time(17, 30, 0))
    c = OpenPeriod(time(19, 0, 0), time(23, 59, 59))
    st1 = StandardOpeningTimes()

    assert st1.any_contradictions() is False

    st1.monday.append(a)
    assert st1.any_contradictions() is False

    st1.closed_days.add("monday")
    assert st1.any_contradictions()

    st1.monday = []
    assert st1.any_contradictions() is False

    st1.saturday = [a, c]
    st1.wednesday = [b]
    assert st1.any_contradictions() is False

    st1.closed_days.add("tuesday")
    assert st1.any_contradictions() is False

    st1.closed_days.add("saturday")
    assert st1.any_contradictions()

    st1.closed_days.add("wednesday")
    assert st1.any_contradictions()
