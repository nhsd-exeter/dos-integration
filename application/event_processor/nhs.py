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

    def get_standard_opening_times(self,opening_time_type) -> list:
        """Get all the Standard Opening Times"""
        standard_filter =  lambda standard: standard["OpeningTimeType"] == opening_time_type and standard["AdditionalOpeningDate"] == ""
        return list(filter(standard_filter, self.OpeningTimes))

    def get_specified_opening_times(self,opening_time_type):
        """Get all the Specified Opening Times"""
        specified_filter =  lambda specified: specified["OpeningTimeType"] == opening_time_type and specified["AdditionalOpeningDate"] != ""
        return list(filter(specified_filter, self.OpeningTimes))
