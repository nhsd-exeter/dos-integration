from datetime import date, datetime
from itertools import groupby
from typing import Dict, List

from aws_lambda_powertools import Logger
from opening_times import WEEKDAYS, OpenPeriod, SpecifiedOpeningTime, StandardOpeningTimes

logger = Logger(child=True)


class NHSEntity:
    """This is an object to store an NHS Entity data

    When passed in a payload (dict) with the NHS data, it will
    pass those fields in to the object as attributes.

    This object may be added to with methods to make the
    comparions with services easier in future tickets.

    """

    CLOSED_AND_HIDDEN_STATUSES = ["Hidden", "Closed"]

    def __init__(self, entity_data: dict) -> None:
        # Set attributes for each value in dict
        self.data = entity_data
        for key, value in entity_data.items():
            setattr(self, key, value)

        self._standard_opening_times = None
        self._specified_opening_times = None

    def __repr__(self) -> str:
        return f"<NHSEntity: name={self.OrganisationName} odscode={self.ODSCode}>:"

    def get_standard_opening_times(self) -> StandardOpeningTimes:
        """[summary]

        Returns:
            StandardOpeningTimes: [description]
        """
        if self._standard_opening_times is None:
            self._standard_opening_times = self._get_standard_opening_times("General")
        return self._standard_opening_times

    def get_specified_opening_times(self) -> List[SpecifiedOpeningTime]:
        """[summary]

        Returns:
            List[SpecifiedOpeningTime]: [description]
        """
        if self._specified_opening_times is None:
            self._specified_opening_times = self._get_specified_opening_times("General")
        return self._specified_opening_times

    def _get_standard_opening_times(self, opening_time_type: str) -> StandardOpeningTimes:
        """Filters the raw opening times data for standard weekly opening
        times and returns it in a StandardOpeningTimes object.

        Args:
            opening_time_type (str): Opening times type (General/Additional)

        Returns:
            StandardOpeningTimes: NHS UK standard opening times
        """
        std_opening_times = StandardOpeningTimes()
        for open_time in self.OpeningTimes:
            # Skips unwanted open times
            if not (
                open_time["Weekday"].lower() in WEEKDAYS
                and open_time["AdditionalOpeningDate"] == ""
                and open_time["OpeningTimeType"] == opening_time_type
                and open_time["IsOpen"]
            ):
                continue

            weekday = open_time["Weekday"].lower()
            start, end = [datetime.strptime(time_str, "%H:%M").time() for time_str in open_time["Times"].split("-")]
            open_period = OpenPeriod(start, end)
            std_opening_times.add_open_period(open_period, weekday)

        return std_opening_times

    def _get_specified_opening_times(self, opening_time_type: str) -> List[SpecifiedOpeningTime]:
        """Get all the Specified Opening Times

        Args:
            opening_time_type (str): OpeningTimeType to filter the data, General for pharmacy

        Returns:
            dict: key=date and value = List[OpenPeriod] objects in a sort order
        """

        # Filter
        def specified_opening_times_filter(specified):
            return specified["OpeningTimeType"] == opening_time_type and specified["AdditionalOpeningDate"] != ""

        specified_times_list = list(filter(specified_opening_times_filter, self.OpeningTimes))

        # Sort the openingtimes data
        sort_specified = sorted(specified_times_list, key=lambda item: (item["AdditionalOpeningDate"], item["Times"]))
        specified_opening_time_dict: Dict[datetime, List[OpenPeriod]] = {}

        # Grouping data by date
        key: date

        for key, value in groupby(sort_specified, lambda item: (item["AdditionalOpeningDate"])):
            op_list: List[OpenPeriod] = []
            for item in list(value):
                start, end = [datetime.strptime(time_str, "%H:%M").time() for time_str in item["Times"].split("-")]
                op_list.append(OpenPeriod(start, end))
                specified_opening_time_dict[key] = op_list

        specified_opening_times = [
            SpecifiedOpeningTime(value, datetime.strptime(key, "%b  %d  %Y").date())
            for key, value in specified_opening_time_dict.items()
        ]

        return specified_opening_times

    def is_status_hidden_or_closed(self) -> bool:
        """Check if the status is hidden or closed. If so, return True

        Returns:
            bool: True if status is hidden or closed, False otherwise
        """
        return self.OrganisationStatus in self.CLOSED_AND_HIDDEN_STATUSES
