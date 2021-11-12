


class NHSEntity:

    def __init__(self, entity_data: dict):
    
        # Set attributes for each value in dict
        for key, value in entity_data.items():
            setattr(self, key, value)

    
    def ods5(self):
        """First 5 digits of odscode"""
        return self.odscode[0:5]