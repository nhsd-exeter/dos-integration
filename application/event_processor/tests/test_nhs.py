import pytest
from random import choices

from nhs import NHSEntity

test_attr_names = ("ODSCode", "Website", "PublicPhone", "Phone", "Postcode")


def test__init__():
    # Arrange
    test_data = {}
    for attr_name in test_attr_names:
        random_str = "".join(choices("ABCDEFGHIJKLM", k=8))
        test_data[attr_name] = random_str
    test_data["OpeningTimes"] = []
    # Act
    nhs_entity = NHSEntity(test_data)
    # Assert
    for attr_name, value in test_data.items():
        assert getattr(nhs_entity, attr_name) == test_data[attr_name]


@pytest.mark.parametrize("opening_time_type, expected", [("General", 1), ("Other", 0)])
def test_get_specified_opening_times(opening_time_type, expected):
    # Arrange
    test_data = {}
    test_data["OpeningTimes"] = [
        {
            "Weekday": "Friday",
            "Times": "08:45-17:00",
            "OffsetOpeningTime": 525,
            "OffsetClosingTime": 1020,
            "OpeningTimeType": "General",
            "AdditionalOpeningDate": "2021-11-12",
            "IsOpen": True
        },
        {
            "Weekday": "Thursday",
            "Times": "08:45-18:00",
            "OffsetOpeningTime": 525,
            "OffsetClosingTime": 1080,
            "OpeningTimeType": "Surgery",
            "AdditionalOpeningDate": "",
            "IsOpen": True
        },
    ]
    nhs_entity = NHSEntity(test_data)
    # Act
    actual = nhs_entity._get_specified_opening_times(opening_time_type)
    # Assert
    assert expected == len(actual), f"Should return {expected} , actually: {len(actual)}"


@pytest.mark.parametrize("opening_time_type, expected", [("General", 1), ("Other", 0)])
def test_get_standard_opening_times(opening_time_type, expected):
    # Arrange
    nhs_entity = NHSEntity({})
    nhs_entity.OpeningTimes = [
        {
            "Weekday": "Friday",
            "Times": "08:45-17:00",
            "OffsetOpeningTime": 525,
            "OffsetClosingTime": 1020,
            "OpeningTimeType": "General",
            "AdditionalOpeningDate": "",
            "IsOpen": True
        },
        {
            "Weekday": "Thursday",
            "Times": "08:45-18:00",
            "OffsetOpeningTime": 525,
            "OffsetClosingTime": 1080,
            "OpeningTimeType": "Surgery",
            "AdditionalOpeningDate": "",
            "IsOpen": True
        },
    ]
    # Act
    actual = nhs_entity._get_standard_opening_times(opening_time_type)
    # Assert
    assert expected == len(actual), f"Should return {expected} , actually: {actual}"
