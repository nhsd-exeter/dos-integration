from random import choices

from event_processor.nhs import NHSEntity

test_attr_names = ("ODSCode", "Website", "PublicPhone", "Phone", "Postcode")


def test__init__():
    # Arrange
    test_data = {}
    for attr_name in test_attr_names:
        random_str = "".join(choices("ABCDEFGHIJKLM", k=8))
        test_data[attr_name] = random_str
    # Act
    nhs_entity = NHSEntity(test_data)
    # Assert
    for attr_name, value in test_data.items():
        assert getattr(nhs_entity, attr_name) == test_data[attr_name]
