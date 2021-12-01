import pytest
from opening_times import OpenPeriod, SpecifiedOpeningTime
from datetime import date,time


@pytest.mark.parametrize("start, end, other_start,other_end, expected",
[(time(8, 0), time(12, 0), time(8, 0), time(12, 0), True), (time(8, 0), time(12, 0), time(13, 0), time(23, 0), False)])
def test_openperiod_eq(start, end, other_start, other_end, expected):
    # Arrange
    open_period = OpenPeriod(start, end)
    # Act
    actual = open_period.__eq__(OpenPeriod(other_start, other_end))
    # Assert
    assert expected == actual, f"Should return {expected} , actually: {actual}"


@pytest.mark.parametrize("start, end, expected", [(time(8, 0), time(12, 0), True), (time(12, 0), time(8, 0), False)])
def test_openperiod_start_before_end(start, end, expected):
    # Arrange
    open_period = OpenPeriod(start, end)
    # Act
    actual = open_period.start_before_end()
    # Assert
    assert expected == actual, f"Should return {expected} , actually: {actual}"


@pytest.mark.parametrize("start, end, other_start,other_end, expected",
[(time(8, 0), time(12, 0), time(8, 0), time(11, 0), True), (time(8, 0), time(12, 0), time(13, 0), time(23, 0), False)])
def test_openperiod_overlaps(start, end, other_start, other_end, expected):
    # Arrange
    open_period = OpenPeriod(start, end)
    # Act
    actual = open_period.overlaps(OpenPeriod(other_start, other_end))
    # Assert
    assert expected == actual, f"Should return {expected} , actually: {actual}"

@pytest.mark.parametrize("open_periods, date, other_open_periods,other_date, expected",
[([OpenPeriod(time(8, 0), time(12, 0)),OpenPeriod(time(13, 0), time(21, 0))],date(2019,5,21),[OpenPeriod(time(8, 0), time(12, 0)),OpenPeriod(time(13, 0), time(21, 0))],date(2019,5,23),False),
([OpenPeriod(time(8, 0), time(12, 0)),OpenPeriod(time(13, 0), time(21, 0))],date(2019,5,23),[OpenPeriod(time(8, 0), time(12, 0)),OpenPeriod(time(13, 0), time(21, 0))],date(2019,5,23),True)])
def test_specified_opening_time_eq(open_periods, date, other_open_periods, other_date, expected):
    # Arrange
    specified_open_period = SpecifiedOpeningTime(open_periods, date)
    # Act
    actual = specified_open_period.__eq__(SpecifiedOpeningTime(other_open_periods, other_date))
    # Assert
    assert expected == actual, f"Should return {expected} , actually: {actual}"


