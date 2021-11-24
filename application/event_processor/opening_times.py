from datetime import time, date
from typing import List

time_format = "%H:%M:%S"
date_format = "%Y/%m/%d"


class OpenPeriod:

    def __init__(self, start: time, end: time) -> None:
        self.start = start
        self.end = end

    def start_string(self):
        return self.start.strftime(time_format)

    def end_string(self):
        return self.end.strftime(time_format)

    def __str__(self):
        return f"{self.start_string()}-{self.end_string()}"

    def __repr__(self):
        return f"<OpenPeriod: {str(self)}>"

    def __eq__(self, other):
        return (isinstance(other, OpenPeriod) and
                self.start == other.start and
                self.end == other.end)

    # A hashing function lets us compare sets correctly later
    def __hash__(self):
        return hash(str(self))


    def start_before_end(self):
        return self.start < self.end

    
    def overlaps(self, other):
        assert self.start_before_end()
        assert other.start_before_end()

        # Q: 'Could two people have met?'
        # A: 'Yes, if both were born before the other died.'
        return (self.start  < other.end and 
                other.start < self.end)
        



class SpecifiedOpeningTime:
    def __init__(self, open_periods: (List[OpenPeriod]), date: (date)) -> None:
        self.open_periods = open_periods
        self.date = date

    def date_string(self):
        return self.date.strftime(date_format)

    def openings_string(self):
        open_period_strings = [str(op) for op in self.open_periods]
        open_period_strings.sort()  # for consitencey
        return f"[{', '.join(open_period_strings)}]"

    def __repr__(self):
        return f"<SpecifiedOpenTime: {self.date_string} "

    def __eq__(self, other):
        return (isinstance(other, SpecifiedOpeningTime) and
                set(self.open_periods) == set(other.open_periods) and
                self.date == other.date)

    def __hash__(self):
        return hash(self.date_string() + self.openings_string())


# TODO: complete later
class StandardOpeningTimes:
    def __init__(self, open_periods: (List[OpenPeriod])) -> None:
        self.open_periods = open_periods

    def __eq__(self, other):
        pass

    def __hash__(self) -> int:
        pass
