from dataclasses import dataclass
from datetime import date, time
from logging import getLogger
from typing import Any, Dict, List

import change_request

logger = getLogger("lambda")
WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")


@dataclass(repr=True, unsafe_hash=True)
class OpenPeriod:
    def __init__(self, start: time, end: time):
        assert isinstance(start, time) and isinstance(end, time)
        self.start = start
        self.end = end

    def start_string(self) -> str:
        return self.start.strftime("%H:%M:%S")

    def end_string(self) -> str:
        return self.end.strftime("%H:%M:%S")

    def __str__(self):
        return f"{self.start_string()}-{self.end_string()}"

    def __eq__(self, other: Any):
        return isinstance(other, OpenPeriod) and self.start == other.start and self.end == other.end

    """ For all comparison methods, check start value first or check
        end value if starts are equal
    """

    def __lt__(self, other: Any):
        if self.start == other.start:
            return self.end < other.end
        return self.start < other.start

    def __gt__(self, other: Any):
        if self.start == other.start:
            return self.end > other.end
        return self.start > other.start

    def start_before_end(self) -> bool:
        return self.start < self.end

    def overlaps(self, other) -> bool:
        assert self.start_before_end()
        assert other.start_before_end()

        return self.start < other.end and other.start < self.end

    def export_cr_format(self) -> Dict[str, str]:
        """Exports open period into a DoS change request accepted format"""
        return {
            "start_time": self.start.strftime(change_request.TIME_FORMAT),
            "end_time": self.end.strftime(change_request.TIME_FORMAT),
        }


@dataclass(unsafe_hash=True)
class SpecifiedOpeningTime:
    def __init__(self, open_periods: (List[OpenPeriod]), specified_date: (date)):
        assert isinstance(specified_date, date)
        self.open_periods = open_periods
        self.date = specified_date

    def date_string(self) -> str:
        return self.date.strftime("%d-%m-%Y")

    def openings_string(self) -> str:
        return open_periods_string(self.open_periods)

    def __repr__(self):
        return f"<SpecifiedOpenTime: {self.date_string()} {self.openings_string()}>"

    def __eq__(self, other):
        return (
            isinstance(other, SpecifiedOpeningTime)
            and self.date == other.date
            and open_periods_equal(self.open_periods, other.open_periods)
        )

    def export_cr_format(self) -> dict:
        """Exports Specified opening time into a DoS change request accepted format"""
        exp_open_periods = [op.export_cr_format() for op in sorted(self.open_periods)]
        date_str = self.date.strftime(change_request.DATE_FORMAT)
        change = {date_str: exp_open_periods}
        return change


@dataclass(unsafe_hash=True)
class StandardOpeningTimes:
    """Represents the standard openings times for a week. Structured as a set of OpenPeriods per day

    monday: [OpenPeriod1, OpenPeriod2]
    tuesday: [OpenPeriod1]
    wednesday: [OpenPeriod1, OpenPeriod2]
    etc etc...

    An empty list that no open periods means CLOSED
    """

    def __init__(self):
        # Initialise all weekday OpenPeriod lists as empty
        for day in WEEKDAYS:
            setattr(self, day, [])

    def __str__(self):
        day_opening_strs = [f"{day}:{open_periods_string(getattr(self, day))}" for day in WEEKDAYS]
        return ", ".join(day_opening_strs)

    def __len__(self):
        return sum([len(getattr(self, day)) for day in WEEKDAYS])

    def __eq__(self, other: Any):
        for day in WEEKDAYS:
            if not open_periods_equal(getattr(self, day), getattr(other, day)):
                return False
        return True

    def add_open_period(self, open_period: OpenPeriod, weekday: str) -> None:
        """Adds a formatted open period to the specified weekda

        Args:
            open_period (OpenPeriod): The open period to add
            weekday (str): The weekday to add the open period to
        """
        if weekday in WEEKDAYS:
            getattr(self, weekday).append(open_period)
        else:
            logger.error(f"Cannot add opening time for invalid weekday '{weekday}', open period not added.")

    def export_cr_format(self) -> Dict[str, List[Dict[str, str]]]:
        """Exports standard opening times into a DoS change request accepted format"""
        change = {}
        for weekday in WEEKDAYS:
            open_periods = sorted(getattr(self, weekday))
            change[weekday.capitalize()] = [op.export_cr_format() for op in open_periods]
        return change


def open_periods_string(open_periods: List[OpenPeriod]) -> str:
    """Returns a string version of a list of open periods in a consistently sorted order

    eg.
    '[08:00:00-13:00:00, 14:00:00-17:00:00, 18:00:00-20:00:00]
    """
    sorted_str_list = [str(op) for op in sorted(list(open_periods))]
    return f"[{', '.join(sorted_str_list)}]"


def any_overlaps(open_periods: List[OpenPeriod]) -> bool:
    """Returns whether any OpenPeriod object in list overlaps any others in the list"""
    untested = open_periods.copy()
    while len(untested) > 1:
        test_op = untested.pop(0)
        for op in untested:
            if test_op.overlaps(op):
                return True
    return False


def any_start_before_end(open_periods: List[OpenPeriod]) -> bool:
    """Returns whether any OpenPeriod object in list starts before it ends"""
    for op in open_periods:
        if op.start_before_end():
            return True
    return False


def spec_open_times_cr_format(spec_opening_dates: List[SpecifiedOpeningTime]) -> dict:
    """Runs the export_cr_format on a list of SpecifiedOpeningTime objects and combines the results"""
    opening_dates_cr_format = {}
    for spec_open_date in spec_opening_dates:
        spec_open_date_payload = spec_open_date.export_cr_format()
        opening_dates_cr_format.update(spec_open_date_payload)
    return opening_dates_cr_format


def open_periods_equal(a: List[OpenPeriod], b: List[OpenPeriod]) -> bool:
    """Checks equality between 2 lists of open periodsRelies on sorting and eq functions in OpenPeriod"""
    return sorted(a) == sorted(b)


def spec_open_times_equal(a: List[SpecifiedOpeningTime], b: List[SpecifiedOpeningTime]) -> bool:
    """Checks equality between 2 lists of SpecifiedOpeningTime Relies on equality,
    and hash functions of SpecifiedOpeningTime"""
    hash_list_a = [hash(a) for a in a]
    hash_list_b = [hash(b) for b in b]
    return sorted(hash_list_a) == sorted(hash_list_b)
