from datetime import datetime,date 
from typing import List,Dict
from application.event_processor.opening_times import SpecifiedOpeningTime
from  event_processor.opening_times import OpenPeriod
from itertools import groupby
from logging import getLogger


logger = getLogger("lambda")


class NHSEntity:
    """This is an object to store an NHS Entity data

    When passed in a payload (dict) with the NHS data, it will
    pass those fields in to the object as attributes.

    This object may be added to with methods to make the
    comparions with services easier in future tickets.

    """

    def __init__(self, entity_data: dict):
        # Set attributes for each value in dict
        for key, value in entity_data.items():
            setattr(self, key, value)

    def get_standard_opening_times(self, opening_time_type) -> list:
        """Get all the Standard Opening Times"""
        def standard_filter(
            standard): return standard["OpeningTimeType"] == opening_time_type and standard["AdditionalOpeningDate"] == ""
        return list(filter(standard_filter, self.OpeningTimes))

    def get_specified_opening_times(self, opening_time_type: str) -> List[SpecifiedOpeningTime]:
        """Get all the Specified Opening Times
        Args:
            opening_time_type  (str): OpeningTimeType to filter the data e.g General for pharmacy
        Returns:
        dict: key=date and value = List[OpenPeriod] objects  in a sort order
        """
        logger.info(f"TODO")

        """filter the raw openingtimes  data"""
        def specified_opening_times_filter(specified):
            return specified["OpeningTimeType"] == opening_time_type and specified["AdditionalOpeningDate"] != ""
        specified_times_list = list(filter(specified_opening_times_filter, self.OpeningTimes))

        """sort the openingtimes  data"""
        sort_specifiled = sorted(specified_times_list, key=lambda item: (
            item["AdditionalOpeningDate"], item['Times']))
        specified_opening_time_dict: Dict[datetime,List[OpenPeriod]] = {}
        """ grouping data by date"""
        key:date
        for key, value in groupby(sort_specifiled, lambda item: (item["AdditionalOpeningDate"])):
            op_list: List[OpenPeriod] = []
            for item in list(value):
                times = str(item["Times"]).split("-")
                op_list.append(OpenPeriod(times[0], times[1]))
                specified_opening_time_dict[key] = op_list
        specified_opening_times = [SpecifiedOpeningTime(value, key) for key, value in specified_opening_time_dict.items()]
        return specified_opening_times
