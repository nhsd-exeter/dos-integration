from dataclasses import dataclass
from datetime import date, time, datetime
from typing import Any, Dict, List, Union

from aws_lambda_powertools import Logger

logger = Logger(child=True)
WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
CHANGE_REQUEST_DATE_FORMAT = "%Y-%m-%d"
CHANGE_REQUEST_TIME_FORMAT = "%H:%M"


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
        return self.start <= other.end and other.start <= self.end

    def export_cr_format(self) -> Union[Dict[str, str], None]:
        """Exports open period into a DoS change request accepted format"""
        return {
            "start_time": self.start.strftime(CHANGE_REQUEST_TIME_FORMAT),
            "end_time": self.end.strftime(CHANGE_REQUEST_TIME_FORMAT),
        }

    @staticmethod
    def any_overlaps(open_periods: List["OpenPeriod"]) -> bool:
        """Returns whether any OpenPeriod object in list overlaps any others in the list"""
        untested = open_periods.copy()
        while len(untested) > 1:
            test_op = untested.pop(0)
            for op in untested:
                if test_op.overlaps(op):
                    return True
        return False

    @staticmethod
    def list_string(open_periods: List["OpenPeriod"]) -> str:
        """Returns a string version of a list of open periods in a consistently sorted order

        eg.
        '[08:00:00-13:00:00, 14:00:00-17:00:00, 18:00:00-20:00:00]
        """
        sorted_str_list = [str(op) for op in sorted(list(open_periods))]
        return f"[{', '.join(sorted_str_list)}]"

    @staticmethod
    def all_start_before_end(open_periods: List["OpenPeriod"]) -> bool:
        """Returns whether all OpenPeriod object in list start before they ends"""
        for op in open_periods:
            if not op.start_before_end():
                return False
        return True

    @staticmethod
    def equal_lists(a: List["OpenPeriod"], b: List["OpenPeriod"]) -> bool:
        """Checks equality between 2 lists of open periodsRelies on sorting and eq functions in OpenPeriod"""
        return sorted(a) == sorted(b)

    @staticmethod
    def from_string(open_period_string: str) -> Union["OpenPeriod", None]:
        """Builds an OpenPeriod object from a string like 12:00-13:00 or 12:00:00-13:00:00"""
        try:
            startime_str, endtime_str = open_period_string.split("-")
            return OpenPeriod.from_string_times(startime_str, endtime_str)
        except (ValueError, AttributeError):
            return None

    @staticmethod
    def from_string_times(opening_time_str: str, closing_time_str: str) -> Union["OpenPeriod", None]:
        """Builds an OpenPeriod object from string time arguments"""
        open_time = string_to_time(opening_time_str)
        close_time = string_to_time(closing_time_str)
        if None in (open_time, close_time):
            return None

        return OpenPeriod(open_time, close_time)


class SpecifiedOpeningTime:
    def __init__(self, open_periods: List[OpenPeriod], specified_date: date, is_open: bool = True):
        assert isinstance(specified_date, date)
        self.open_periods = open_periods
        self.date = specified_date
        self.is_open = is_open

    def date_string(self) -> str:
        return self.date.strftime("%d-%m-%Y")

    def open_periods_string(self) -> str:
        return OpenPeriod.list_string(self.open_periods)

    def __hash__(self):
        return hash((tuple(sorted(self.open_periods)), self.date, self.is_open))

    def __repr__(self):
        return f"<SpecifiedOpenTime: {self.date_string()} open={self.is_open} {self.open_periods_string()}>"

    def __str__(self):
        return f"{self.open_string()} on {self.date_string()} {self.open_periods_string()}"

    def open_string(self):
        if self.is_open:
            return "OPEN"
        return "CLOSED"

    def __eq__(self, other):
        return (
            isinstance(other, SpecifiedOpeningTime)
            and self.is_open == other.is_open
            and self.date == other.date
            and OpenPeriod.equal_lists(self.open_periods, other.open_periods)
        )

    def export_cr_format(self) -> dict:
        """Exports Specified opening time into a DoS change request accepted format"""
        exp_open_periods = [op.export_cr_format() for op in sorted(self.open_periods)]
        date_str = self.date.strftime(CHANGE_REQUEST_DATE_FORMAT)
        change = {date_str: exp_open_periods}
        return change

    def contradiction(self) -> bool:
        """Returns whether the open flag contradicts the number of open periods present."""
        return self.is_open != (len(self.open_periods) > 0)

    def any_overlaps(self) -> bool:
        return OpenPeriod.any_overlaps(self.open_periods)

    def all_start_before_end(self) -> bool:
        return OpenPeriod.all_start_before_end(self.open_periods)

    def is_valid(self) -> bool:
        """Validates no overlaps, 'starts before ends' and contradictions."""
        return self.all_start_before_end() and (not self.any_overlaps()) and (not self.contradiction())

    @staticmethod
    def export_cr_format_list(spec_opening_dates: List["SpecifiedOpeningTime"]) -> dict:
        """Runs the export_cr_format on a list of SpecifiedOpeningTime objects and combines the results"""
        opening_dates_cr_format = {}
        for spec_open_date in spec_opening_dates:
            spec_open_date_payload = spec_open_date.export_cr_format()
            opening_dates_cr_format.update(spec_open_date_payload)
        return opening_dates_cr_format

    @staticmethod
    def equal_lists(a: List["SpecifiedOpeningTime"], b: List["SpecifiedOpeningTime"]) -> bool:
        """Checks equality between 2 lists of SpecifiedOpeningTime Relies on equality,
        and hash functions of SpecifiedOpeningTime"""
        hash_list_a = [hash(a) for a in a]
        hash_list_b = [hash(b) for b in b]
        return sorted(hash_list_a) == sorted(hash_list_b)

    @staticmethod
    def valid_list(list: List["SpecifiedOpeningTime"]) -> bool:
        return all([x.is_valid() for x in list])

    @staticmethod
    def from_list(list: List["SpecifiedOpeningTime"], chosen_date: date, default=None) -> bool:
        for item in list:
            if item.date == chosen_date:
                return item
        return default


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
        self.generic_bankholiday = []
        self.explicit_closed_days = set()

    def __repr__(self):
        closed_days_str = ""
        if len(self.explicit_closed_days) > 0:
            closed_days_str = f" exp_closed_days={self.explicit_closed_days}"

        return f"<StandardOpeningTimes: {str(self)}{closed_days_str}>"

    def __str__(self):
        return self.to_string(", ")

    def __len__(self):
        return sum([len(getattr(self, day)) for day in WEEKDAYS])

    def __eq__(self, other: "StandardOpeningTimes"):
        """Check equality of 2 StandardOpeningTimes (generic bankholiday values are ignored)"""

        if not isinstance(other, StandardOpeningTimes):
            return False

        if self.all_closed_days() != other.all_closed_days():
            return False

        for day in WEEKDAYS:
            if not OpenPeriod.equal_lists(self.get_openings(day), other.get_openings(day)):
                return False

        return True

    def to_string(self, seperator: str = ", ") -> str:
        return seperator.join([f"{day}={OpenPeriod.list_string(getattr(self, day))}" for day in WEEKDAYS])

    def get_openings(self, day: str) -> List[OpenPeriod]:
        return getattr(self, day.lower())

    def all_closed_days(self) -> List[str]:
        """Returns a set of all implicit AND explicit closed days."""
        all_closed_days = self.explicit_closed_days

        # Add implicit closed days to explicit set
        for day in WEEKDAYS:
            if len(getattr(self, day)) == 0:
                all_closed_days.add(day)

        return all_closed_days

    def is_open(self, weekday: str) -> bool:
        return len(getattr(self, weekday)) > 0

    def same_openings(self, other: "StandardOpeningTimes", day: str) -> bool:
        return OpenPeriod.equal_lists(self.get_openings(day), other.get_openings(day))

    def add_open_period(self, open_period: OpenPeriod, weekday: str) -> None:
        """Adds a formatted open period to the specified weekda

        Args:
            open_period (OpenPeriod): The open period to add
            weekday (str): The weekday to add the open period to
        """
        day_key = weekday.lower()
        if day_key in WEEKDAYS:
            getattr(self, day_key).append(open_period)
        elif day_key == "bankholiday":
            logger.warning(f"A generic bank holiday OpenPeriod '{open_period}' was found. This will be ignored.")
            self.generic_bankholiday.append(open_period)
        else:
            logger.error(f"Cannot add opening time for invalid weekday '{weekday}', open period not added.")

    def any_overlaps(self):
        for weekday in WEEKDAYS:
            if OpenPeriod.any_overlaps(getattr(self, weekday)):
                return True
        return False

    def all_start_before_end(self):
        for weekday in WEEKDAYS:
            if not OpenPeriod.all_start_before_end(getattr(self, weekday)):
                return False
        return True

    def any_contradictions(self) -> bool:
        """Returns True if any open period falls on a day that is marked as closed."""
        for weekday in self.explicit_closed_days:
            if self.is_open(weekday):
                return True
        return False

    def is_valid(self) -> bool:
        return self.all_start_before_end() and not self.any_overlaps() and not self.any_contradictions()

    def export_cr_format(self) -> Dict[str, List[Dict[str, str]]]:
        """Exports standard opening times into a DoS change request accepted format"""
        change = {}
        for weekday in WEEKDAYS:
            open_periods = sorted(getattr(self, weekday))
            change[weekday.capitalize()] = [op.export_cr_format() for op in open_periods]
        return change


def string_to_time(time_str: str) -> time:
    for time_format in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(str(time_str), time_format).time()
        except ValueError:
            pass
    return None
