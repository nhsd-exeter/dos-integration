from datetime import time, date
from typing import List
from logging import getLogger

logger = getLogger("lambda")

TIME_FORMAT = "%H:%M:%S"
DATE_FORMAT = "%Y/%m/%d"
WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", 
            "friday", "saturday", "sunday")


class OpenPeriod:

    def __init__(self, start: time, end: time):
        self.start = start
        self.end = end

    def start_string(self):
        return self.start.strftime(TIME_FORMAT)

    def end_string(self):
        return self.end.strftime(TIME_FORMAT)

    def __str__(self):
        return f"{self.start_string()}-{self.end_string()}"

    def __repr__(self):
        return f"<OpenPeriod: {str(self)}>"

    def __eq__(self, other):
        return (isinstance(other, OpenPeriod) and
                self.start == other.start and
                self.end == other.end)

    """ For all comparison methods, check start value first or check
        end value if starts are equal
    """
    def __lt__(self, other):
        if self.start == other.start:
            return self.end < other.end
        return self.start < other.start

    def __gt__(self, other):
        if self.start == other.start:
            return self.end > other.end
        return self.start > other.start

    # A hashing function lets us compare sets correctly later
    def __hash__(self):
        return hash(str(self))


    def start_before_end(self):
        return self.start < self.end

    
    def overlaps(self, other):
        assert self.start_before_end()
        assert other.start_before_end()

        # "2 people can meet if both were born before the other dies"
        return (self.start  < other.end and 
                other.start < self.end)
        



class SpecifiedOpeningTime:
    def __init__(self, open_periods: (List[OpenPeriod]), date: (date)):
        self.open_periods = open_periods
        self.date = date

    def date_string(self):
        return self.date.strftime(DATE_FORMAT)

    def openings_string(self):
        return open_periods_string(self.open_periods)

    def __repr__(self):
        return (f"<SpecifiedOpenTime: {self.date_string()} "
                f"{self.openings_string()}>")

    def __eq__(self, other):
        return (isinstance(other, SpecifiedOpeningTime) and
                set(self.open_periods) == set(other.open_periods) and
                self.date == other.date)

    def __hash__(self):
        return hash(self.date_string() + self.openings_string())




class StandardOpeningTimes:
    """ Represents the standard openings times for a week. Structured as a
        set of OpenPeriods per day

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
        day_opening_strs = [f"{day}:{open_periods_string(getattr(self, day))}"
                            for day in WEEKDAYS]
        return " ".join(day_opening_strs)

    def __eq__(self, other):
        for day in WEEKDAYS:
            if getattr(self, day) != getattr(other, day):
                return False
        return True

    def __hash__(self) -> int:
        return hash(str(self))


    def add_open_period(self, open_period, weekday):
        if weekday in WEEKDAYS:
            getattr(self, weekday).append(open_period)
        else:
            logger.error(f"Cannot add opening time for invalid weekday "
                         f"'{weekday}', open period not added.")


def open_periods_string(open_periods):
    """ Returns a string version of a list of open periods in
        a consistently sorted order.

        eg.
        '[08:00:00-13:00:00, 14:00:00-17:00:00, 18:00:00-20:00:00]
    """
    sorted_str_list = [str(op) for op in sorted(list(open_periods))]
    return f"[{', '.join(sorted_str_list)}]"


def any_overlaps(open_periods):
    """ Returns whether any OpenPeriod object in list overlaps
        any others in the list.
    """
    untested = open_periods.copy()
    while len(untested) > 1:
        test_op = untested.pop(0)
        for op in untested:
            if test_op.overlaps(op):
                return True
    return False

def any_start_before_end(open_periods):
    """ Returns whether any OpenPeriod object in list starts 
        before it ends.
    """
    for op in open_periods:
        if op.start_before_end():
            return True
    return False




