import pytest
from random import choices
from datetime import time, date


from ..nhs import NHSEntity
from opening_times import OpenPeriod, SpecifiedOpeningTime, StandardOpeningTimes

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



def test_get_specified_opening_times():
    # Arrange
    nhs_entity = NHSEntity({
        "OpeningTimes": [
        {
            "Weekday": "",
            "Times": "08:45-17:00",
            "OffsetOpeningTime": 525,
            "OffsetClosingTime": 1020,
            "OpeningTimeType": "Additional",
            "AdditionalOpeningDate": "Nov 12 2021",
            "IsOpen": True,
        },
        {
            "Weekday": "",
            "Times": "09:00-16:00",
            "OffsetOpeningTime": 540,
            "OffsetClosingTime": 980,
            "OpeningTimeType": "Additional",
            "AdditionalOpeningDate": "Jan  6    2022",
            "IsOpen": True,
        },
        {
            "Weekday": "",
            "Times": "09:00-16:00",
            "OffsetOpeningTime": 540,
            "OffsetClosingTime": 980,
            "OpeningTimeType": "Additional",
            "AdditionalOpeningDate": "Apr  01   2023",
            "IsOpen": True,
        },
        {
            "Weekday": "Thursday",
            "Times": "08:45-18:00",
            "OffsetOpeningTime": 525,
            "OffsetClosingTime": 1080,
            "OpeningTimeType": "General",
            "AdditionalOpeningDate": "",
            "IsOpen": True,
        },
    ]})
    # Act
    # Assert
    
    expected = [
        SpecifiedOpeningTime([OpenPeriod(time(8, 45, 0), time(17, 0, 0))], date(2021, 11, 12)),
        SpecifiedOpeningTime([OpenPeriod(time(9, 0, 0), time(16, 0, 0))], date(2022, 1, 6)),
        SpecifiedOpeningTime([OpenPeriod(time(9, 0, 0), time(16, 0, 0))], date(2023, 4, 1))
    ]

    actual_spec_open_times = nhs_entity.specified_opening_times
    assert len(actual_spec_open_times) == len(expected),(
        f"Should return {len(expected)} , actually: {len(spec_open_times)}")
    
    for exp_spec_open_time in expected:
        assert exp_spec_open_time in actual_spec_open_times, (
            f"NHS entity should contain {exp_spec_open_time} but can't be found in list {actual_spec_open_times}")


def test_get_standard_opening_times():
    # Arrange
    nhs_entity = NHSEntity({
        "OpeningTimes": [
            {
                "Weekday": "Friday",
                "Times": "08:45-17:00",
                "OpeningTimeType": "General",
                "AdditionalOpeningDate": "",
                "IsOpen": True,
            },
            {
                "Weekday": "",
                "Times": "08:45-18:00",
                "OpeningTimeType": "Additional",
                "AdditionalOpeningDate": "23 Jan 2022",
                "IsOpen": True,
            },
            {
                "Weekday": "Thursday",
                "Times": "09:00-17:00",
                "OpeningTimeType": "General",
                "AdditionalOpeningDate": "",
                "IsOpen": True,
            },
            {
                "Weekday": "Saturday",
                "Times": "08:45-18:00",
                "OpeningTimeType": "Invalid_Type",
                "AdditionalOpeningDate": "",
                "IsOpen": True,
            },
        ]})
    # Act
    expected_std_open_times = StandardOpeningTimes()
    expected_std_open_times.friday.append(OpenPeriod(time(8, 45, 0), time(17, 0, 0)))
    expected_std_open_times.thursday.append(OpenPeriod(time(9, 0, 0), time(17, 0, 0)))

    actual_std_open_times = nhs_entity.standard_opening_times

    # Assert
    assert actual_std_open_times == expected_std_open_times, (
        f"Actual std openings differ from expected. Actual={actual_std_open_times} "
        f"and Expected: {expected_std_open_times}")


@pytest.mark.parametrize("organisation_status", ["Visible", "OTHER"])
def test_is_status_hidden_or_closed_open_service(organisation_status: str):
    # Arrange
    test_data = {"OrganisationStatus": organisation_status}
    nhs_entity = NHSEntity(test_data)
    # Act
    result = nhs_entity.is_status_hidden_or_closed()
    # Assert
    assert not result


@pytest.mark.parametrize("organisation_status", NHSEntity.CLOSED_AND_HIDDEN_STATUSES)
def test_is_status_hidden_or_closed_not_open_service(organisation_status: str):
    # Arrange
    test_data = {"OrganisationStatus": organisation_status}
    nhs_entity = NHSEntity(test_data)
    # Act
    result = nhs_entity.is_status_hidden_or_closed()
    # Assert
    assert result
