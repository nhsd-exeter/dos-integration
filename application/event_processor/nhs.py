


class NHSEntity:
    """ This is an object to store an NHS Entity data

        When passed in a payload (dict) with the NHS data, it will
        pass those fields in to the object as attributes.

        This object may be added to with methods to make the 
        comparions with services easier in future tickets.
    
    """

    def __init__(self, entity_data: dict):
    
        # Set attributes for each value in dict
        for key, value in entity_data.items():
            setattr(self, key, value)

    
    def ods5(self):
        """First 5 digits of odscode"""
        return self.odscode[0:5]