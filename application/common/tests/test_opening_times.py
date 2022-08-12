from datetime import date, datetime, time, timedelta

import pytest

from ..opening_times import OpenPeriod, SpecifiedOpeningTime, StandardOpeningTimes

OP = OpenPeriod.from_string


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


def test_open_period_eq_hash():
    a = OP("9:00-17:00")
    a2 = OP("9:00:00-17:00:00")
    b = OP("09:00-16:00")
    b2 = OP("9:00-16:00")
    c = OP("02:00-16:00:00")
    d = OP("09:00-17:00:01")

    assert a == a2
    assert hash(a) == hash(a2)

    assert a != b
    assert hash(a) != hash(b)

    assert a != c
    assert hash(a) != hash(c)

    assert b == b2
    assert hash(b) == hash(b2)

    assert b != c
    assert hash(b) != hash(c)

    assert c != d
    assert hash(c) != hash(d)

    assert d == d
    assert hash(d) == hash(d)

    b.end = time(17, 0, 0)
    assert a == b
    assert hash(a) == hash(b)

    a.start = time(3, 0, 0)
    assert a != a2
    assert hash(a) != hash(a2)


@pytest.mark.parametrize("start, end, expected", [(time(8, 0), time(12, 0), True), (time(12, 0), time(8, 0), False)])
def test_open_period_start_before_end(start, end, expected):
    # Arrange
    open_period = OpenPeriod(start, end)
    # Act
    actual = open_period.start_before_end()
    # Assert
    assert expected == actual, f"Should return {expected} , actually: {actual}"


def test_openperiod_overlaps():
    assert OP("08:00-12:00").overlaps(OP("13:00-17:00")) is False
    assert OP("08:00-12:00").overlaps(OP("12:01-17:00")) is False
    assert OP("08:00:00-12:00:00").overlaps(OP("12:00:01-17:00:00")) is False
    assert OP("13:00-17:00").overlaps(OP("08:00-12:00")) is False
    assert OP("08:00-12:59").overlaps(OP("13:00-17:00")) is False
    assert OP("12:40-15:23").overlaps(OP("18:03-22:16")) is False

    assert OP("08:00-12:00").overlaps(OP("12:00-17:00"))
    assert OP("08:00-12:00").overlaps(OP("12:00-17:00"))
    assert OP("08:00-12:00").overlaps(OP("10:00-17:00"))
    assert OP("00:00-23:59").overlaps(OP("00:00-23:59"))
    assert OP("08:00-12:00").overlaps(OP("07:00-17:00"))
    assert OP("01:00-23:00").overlaps(OP("10:00-17:00"))


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
    a2 = OpenPeriod(time(8, 0, 0), time(12, 0, 0))

    assert OpenPeriod.equal_lists([a], [a])
    assert OpenPeriod.equal_lists([a, b], [a, b])
    assert OpenPeriod.equal_lists([a2, c], [a, c])
    assert OpenPeriod.equal_lists([b, c], [c, b])
    assert OpenPeriod.equal_lists([a, b, c], [a2, b, c])
    assert OpenPeriod.equal_lists([a, b, c], [c, b, a])
    assert OpenPeriod.equal_lists([a2, c, c], [c, a, c])

    assert not OpenPeriod.equal_lists([a], [b])
    assert not OpenPeriod.equal_lists([a, b, c], [a, b])
    assert not OpenPeriod.equal_lists([c, c], [a, c])
    assert not OpenPeriod.equal_lists([b, c], [])
    assert not OpenPeriod.equal_lists([a, b, c], [a2, b, a2])
    assert not OpenPeriod.equal_lists([a, b, c], [a])


def test_open_period__lt__gt__():
    a = OpenPeriod(time(8, 0, 0), time(12, 0, 0))
    a2 = OpenPeriod(time(8, 0, 0), time(12, 0, 0))
    b = OpenPeriod(time(9, 0, 0), time(12, 0, 0))
    c = OpenPeriod(time(8, 0, 1), time(12, 0, 0))
    d = OpenPeriod(time(8, 0, 0), time(12, 0, 1))
    e = OpenPeriod(time(8, 0, 0), time(13, 0, 0))

    assert a < b
    assert b > a
    assert a < c
    assert c > a
    assert a < d
    assert d > a
    assert a < e
    assert e > a
    assert not a < a2
    assert not a > a2
    assert not a2 < a
    assert not a2 > a


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


def test_openperiod_from_string():
    a = OpenPeriod.from_string("08:34-15:13")
    assert a.start == time(8, 34, 0)
    assert a.end == time(15, 13, 0)

    b = OpenPeriod.from_string("04:45:55-09:32:22")
    assert b.start == time(4, 45, 55)
    assert b.end == time(9, 32, 22)

    c = OpenPeriod.from_string("00:00:00-09:32:22")
    assert c.start == time(0, 0, 0)
    assert c.end == time(9, 32, 22)

    d = OpenPeriod.from_string("00:00-23:59")
    assert d.start == time(0, 0, 0)
    assert d.end == time(23, 59, 00)

    assert OpenPeriod.from_string("") is None
    assert OpenPeriod.from_string("hello") is None
    assert OpenPeriod.from_string("12:0015:32") is None
    assert OpenPeriod.from_string("12:00 15:32") is None
    assert OpenPeriod.from_string("12:00") is None
    assert OpenPeriod.from_string("08:00-24:00") is None
    assert OpenPeriod.from_string("38:00-12:00") is None
    assert OpenPeriod.from_string("08:00-44:00") is None
    assert OpenPeriod.from_string("08:0044:00") is None
    assert OpenPeriod.from_string("08:00-44:00-08:00") is None
    assert OpenPeriod.from_string(231892) is None
    assert OpenPeriod.from_string(None) is None
    assert OpenPeriod.from_string(2.38) is None


def test_openperiod_from_string_times():
    a = OpenPeriod.from_string_times("08:34", "15:13")
    assert a.start == time(8, 34, 0)
    assert a.end == time(15, 13, 0)

    b = OpenPeriod.from_string_times("04:45:55", "09:32:22")
    assert b.start == time(4, 45, 55)
    assert b.end == time(9, 32, 22)

    c = OpenPeriod.from_string_times("00:00:00", "09:32")
    assert c.start == time(0, 0, 0)
    assert c.end == time(9, 32, 0)

    d = OpenPeriod.from_string_times("00:00", "23:59")
    assert d.start == time(0, 0, 0)
    assert d.end == time(23, 59, 00)

    e = OpenPeriod.from_string_times("00:00:05", "23:59")
    assert e.start == time(0, 0, 5)
    assert e.end == time(23, 59, 00)

    d = OpenPeriod.from_string_times("00:00", "23:59")
    assert d.start == time(0, 0, 0)
    assert d.end == time(23, 59, 00)

    assert OpenPeriod.from_string_times("", "") is None
    assert OpenPeriod.from_string_times("hello", "hello") is None
    assert OpenPeriod.from_string_times("12:00", "32") is None
    assert OpenPeriod.from_string_times("", "15:32") is None
    assert OpenPeriod.from_string_times("08:00", "24:00") is None
    assert OpenPeriod.from_string_times("38:00", "12:00") is None
    assert OpenPeriod.from_string_times("08:00", "44:00") is None
    assert OpenPeriod.from_string_times(231892, 12323) is None
    assert OpenPeriod.from_string_times(None, None) is None
    assert OpenPeriod.from_string_times(2.38, "03:00") is None


def test_open_period_export_test_format():
    assert OpenPeriod(time(8, 0, 0), time(15, 0, 0)).export_test_format() == {
        "start_time": "08:00",
        "end_time": "15:00",
    }
    assert OpenPeriod(time(0, 0, 0), time(15, 0, 0)).export_test_format() == {
        "start_time": "00:00",
        "end_time": "15:00",
    }
    assert OpenPeriod(time(8, 0, 0), time(23, 59, 0)).export_test_format() == {
        "start_time": "08:00",
        "end_time": "23:59",
    }
    assert OpenPeriod(time(8, 0, 0), time(23, 59, 59)).export_test_format() == {
        "start_time": "08:00",
        "end_time": "23:59",
    }
    assert OpenPeriod(time(0, 0, 0), time(23, 59, 59)).export_test_format() == {
        "start_time": "00:00",
        "end_time": "23:59",
    }
    assert OpenPeriod(time(1, 2, 3), time(4, 5, 0)).export_test_format() == {"start_time": "01:02", "end_time": "04:05"}
    assert OpenPeriod(time(13, 35, 0), time(13, 36, 0)).export_test_format() == {
        "start_time": "13:35",
        "end_time": "13:36",
    }


def test_specifiedopeningtime_eq_and_hash():
    op1 = OpenPeriod(time(8, 0, 0), time(12, 0, 0))
    op2 = OpenPeriod(time(13, 0, 0), time(17, 30, 0))
    op3 = OpenPeriod(time(19, 0, 0), time(23, 30, 0))

    d1 = date(2021, 12, 24)
    d2 = date(2021, 12, 28)
    d2b = date(2021, 12, 28)

    sp1 = SpecifiedOpeningTime([], d1, is_open=False)
    sp1b = SpecifiedOpeningTime([], d1, is_open=False)
    sp2 = SpecifiedOpeningTime([op1, op2, op3], d1)
    sp2b = SpecifiedOpeningTime([op3, op2, op1], d1)
    sp3 = SpecifiedOpeningTime([op2, op3], d2)
    sp3b = SpecifiedOpeningTime([op3, op2], d2b)
    sp4 = SpecifiedOpeningTime([op1], d2)

    assert sp1 == sp1b
    assert hash(sp1) == hash(sp1b)
    assert sp2 == sp2b
    assert hash(sp2) == hash(sp2b)
    assert sp3 == sp3b
    assert hash(sp3) == hash(sp3b)

    assert sp1 != sp2
    assert hash(sp1) != hash(sp2)
    assert sp2 != sp3
    assert hash(sp2) != hash(sp3)
    assert sp1 != sp3
    assert hash(sp1) != hash(sp3)
    assert sp3 != sp4
    assert hash(sp3) != hash(sp4)


def test_specifiedopeningtime_open_string():
    s = SpecifiedOpeningTime([], date(2020, 5, 5), is_open=True)
    assert s.open_string() == "OPEN"

    s.is_open = False
    assert s.open_string() == "CLOSED"


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
    d = OpenPeriod(time(9, 0, 0), time(18, 30, 0))  # Overlaps
    e = OpenPeriod(time(9, 0, 0), time(2, 30, 0))  # Start not before end

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
    sp4 = SpecifiedOpeningTime([c], date(2021, 12, 24))

    assert sp1 != sp2
    assert sp1 != sp3
    assert sp2 != sp3
    assert sp2 == sp2b

    assert SpecifiedOpeningTime.equal_lists([], [])
    assert SpecifiedOpeningTime.equal_lists([sp1], [sp1])
    assert SpecifiedOpeningTime.equal_lists([sp1, sp2], [sp1, sp2])
    assert SpecifiedOpeningTime.equal_lists([sp1, sp2, sp3], [sp1, sp2, sp3])
    assert SpecifiedOpeningTime.equal_lists([sp1, sp2, sp3], [sp2, sp3, sp1])
    assert SpecifiedOpeningTime.equal_lists([sp1, sp2], [sp2, sp1])
    assert SpecifiedOpeningTime.equal_lists([sp1, sp2, sp3], [sp2b, sp3, sp1])
    assert SpecifiedOpeningTime.equal_lists([sp2], [sp2b])

    assert not SpecifiedOpeningTime.equal_lists([], [sp1])
    assert not SpecifiedOpeningTime.equal_lists([sp1], [sp2])
    assert not SpecifiedOpeningTime.equal_lists([sp1, sp1], [sp1, sp2])
    assert not SpecifiedOpeningTime.equal_lists([sp3], [])
    assert not SpecifiedOpeningTime.equal_lists([sp1, sp2, sp3], [sp1, sp1, sp3])
    assert not SpecifiedOpeningTime.equal_lists([sp1, sp2, sp3, sp3], [sp1, sp2, sp3])
    assert not SpecifiedOpeningTime.equal_lists([sp3], [sp4])
    assert not SpecifiedOpeningTime.equal_lists([sp1, sp3], [sp1, sp4])


def test_specifiedopentimes_remove_past_dates():
    a = OpenPeriod(time(8, 0, 0), time(12, 0, 0))
    b = OpenPeriod(time(13, 0, 0), time(17, 30, 0))
    c = OpenPeriod(time(19, 0, 0), time(23, 30, 0))

    now_date = datetime.now().date()

    future1 = SpecifiedOpeningTime([], (now_date + timedelta(weeks=4)), is_open=False)
    future2 = SpecifiedOpeningTime([a, b, c], (now_date + timedelta(weeks=5)))
    past = SpecifiedOpeningTime([b], (now_date - timedelta(weeks=4)))

    assert SpecifiedOpeningTime.remove_past_dates(list=[future1, future2, past]) == [future1, future2]


def test_specifiedopentime_export_service_history_format_open():
    # Arrange
    a = OpenPeriod(time(8, 0, 0), time(12, 0, 0))
    b = OpenPeriod(time(13, 0, 0), time(17, 30, 0))
    c = OpenPeriod(time(19, 0, 0), time(23, 30, 0))
    specified_opening_time = SpecifiedOpeningTime([a, b, c], date(2021, 12, 24), is_open=True)
    # Act
    result = specified_opening_time.export_service_history_format()
    # Assert
    assert [
        "2021-12-24-28800-43200",
        "2021-12-24-46800-63000",
        "2021-12-24-68400-84600",
    ] == result


def test_specifiedopentime_export_service_history_format_closed():
    # Arrange
    specified_opening_time = SpecifiedOpeningTime([], date(2021, 12, 24), is_open=False)
    # Act
    result = specified_opening_time.export_service_history_format()
    # Assert
    assert ["2021-12-24-closed"] == result


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
def test_specified_opening_time_export_test_format(expected: dict, actual: SpecifiedOpeningTime):
    test_format = actual.export_test_format()
    assert test_format == expected, f"expected {expected} SpecifiedOpeningTime change req format but got {test_format}"


def test_stdopeningtimes_eq_len():
    a = OpenPeriod(time(8, 0, 0), time(12, 0, 0))
    b = OpenPeriod(time(13, 0, 0), time(17, 30, 0))
    c = OpenPeriod(time(19, 0, 0), time(23, 59, 59))
    st1 = StandardOpeningTimes()
    st2 = StandardOpeningTimes()

    assert st1 == st2
    assert st1 != 23
    assert st1 != "Harry Potter"

    st1.monday.append(a)
    assert st1 != st2
    assert len(st1) == 1

    st2.monday.append(a)
    assert st1 == st2
    assert len(st2) == 1

    st2.friday += [a, b, c]
    st1.friday += [a, b]
    assert st1 != st2
    assert len(st1) == 3
    assert len(st2) == 4

    st1.friday.append(c)
    assert st1 == st2
    assert len(st1) == 4

    st1.sunday += [b, a, c]
    st2.sunday += [c, b, a]
    assert st1 == st2
    assert len(st1) == 7
    assert len(st2) == 7

    st1.friday = []
    st2.friday = []
    assert len(st1) == 4
    assert len(st1) == 4

    # Standard opening times should be equal even if generic bank holidays are not
    # this is expected behaviour because generic bank holidays in DoS are ignored.
    st1.generic_bankholiday = [a]
    st2.generic_bankholiday = []
    assert st1 == st2

    st1.generic_bankholiday = [a, b, c]
    st2.generic_bankholiday = [a, b, c]
    assert st1 == st2


def test_stdopeningtimes_any_contradiction():
    a = OpenPeriod(time(8, 0, 0), time(12, 0, 0))
    b = OpenPeriod(time(13, 0, 0), time(17, 30, 0))
    c = OpenPeriod(time(19, 0, 0), time(23, 59, 59))
    st1 = StandardOpeningTimes()

    assert st1.any_contradictions() is False

    st1.monday.append(a)
    assert st1.any_contradictions() is False

    st1.explicit_closed_days.add("monday")
    assert st1.any_contradictions()

    st1.monday = []
    assert st1.any_contradictions() is False

    st1.saturday = [a, c]
    st1.wednesday = [b]
    assert st1.any_contradictions() is False

    st1.explicit_closed_days.add("tuesday")
    assert st1.any_contradictions() is False

    st1.explicit_closed_days.add("saturday")
    assert st1.any_contradictions()

    st1.explicit_closed_days.add("wednesday")
    assert st1.any_contradictions()


def test_stdopeningtimes_export_opening_times_for_day():
    # Arrange
    a = OpenPeriod(time(8, 0, 0), time(12, 0, 0))
    b = OpenPeriod(time(13, 0, 0), time(18, 0, 0))
    st1 = StandardOpeningTimes()
    st1.add_open_period(a, "monday")
    st1.add_open_period(b, "monday")
    # Act
    response = st1.export_opening_times_for_day("monday")
    # Assert
    assert ["08:00-12:00", "13:00-18:00"] == response


def test_stdopeningtimes_export_opening_times_in_seconds_for_day():
    # Arrange
    a = OpenPeriod(time(9, 0, 0), time(13, 0, 0))
    b = OpenPeriod(time(14, 0, 0), time(19, 0, 0))
    st1 = StandardOpeningTimes()
    st1.add_open_period(a, "monday")
    st1.add_open_period(b, "monday")
    # Act
    response = st1.export_opening_times_in_seconds_for_day("monday")
    # Assert
    assert ["32400-46800", "50400-68400"] == response


def test_standard_opening_times_export_test_format():

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
    assert std_opening_times.export_test_format() == expected

    # Add single opening time for monday
    std_opening_times.monday.append(OpenPeriod(time(8, 0, 0), time(15, 0, 0)))
    expected["Monday"].append({"start_time": "08:00", "end_time": "15:00"})
    assert std_opening_times.export_test_format() == expected

    # Add another to tuesday
    std_opening_times.tuesday.append(OpenPeriod(time(8, 0, 0), time(20, 0, 0)))
    expected["Tuesday"].append({"start_time": "08:00", "end_time": "20:00"})
    assert std_opening_times.export_test_format() == expected

    # Add another to monday
    std_opening_times.monday.append(OpenPeriod(time(16, 0, 0), time(20, 0, 0)))
    expected["Monday"].append({"start_time": "16:00", "end_time": "20:00"})
    assert std_opening_times.export_test_format() == expected

    # Add to every other day
    for day in ["Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        getattr(std_opening_times, day.lower()).append(OpenPeriod(time(16, 0, 0), time(20, 0, 0)))
        expected[day].append({"start_time": "16:00", "end_time": "20:00"})
    assert std_opening_times.export_test_format() == expected
