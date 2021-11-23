from datetime import datetime
from typing import List


class OpenPeriod:

    def __init__(self, start: datetime.time, end: datetime.time) -> None:
        self.start = start
        self.end = end

    def __eq__(self, other) -> bool:
        if isinstance(other, OpenPeriod):
            return self.start == other.start and self.end == other.end
        return False


class SpecififedOpeningTime:
    def __init__(self, open_periods: (List[OpenPeriod]), date: (datetime.date)) -> None:
        self.open_periods = open_periods
        self.date = date

    def __eq__(self, other) -> bool:
        pass

    def __hash__(self) -> int:
        pass


class StandardOpeningTimes:
    def __init__(self, open_periods: (dict(List[OpenPeriod]))) -> None:
        self.open_periods = open_periods

    def __eq__(self, other) -> bool:
        pass

    def __hash__(self) -> int:
        pass
