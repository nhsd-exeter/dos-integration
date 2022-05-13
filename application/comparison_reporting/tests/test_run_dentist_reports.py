from unittest.mock import patch
from datetime import date

from common.opening_times import OpenPeriod, SpecifiedOpeningTime, StandardOpeningTimes

OP = OpenPeriod.from_string


@patch("comparison_reporting.reporter.download_csv_as_dicts")
def test_get_dentists(mock_download_csv_as_dicts):
    from comparison_reporting.run_dentist_reports import get_dentists

    mock_download_csv_as_dicts.side_effect = [
        [
            {
                "OrganisationID": 111,
                "OrganisationCode": "V001111",
                "OrganisationType": "Dentists",
                "SubType": "UNKNOWN",
                "OrganisationStatus": "Visible",
                "OrganisationName": "Fake Dentist 1",
                "Address1": "1 Fake Street",
                "Address2": "",
                "Address3": "",
                "City": "Fake Town",
                "County": "Fake County",
                "Postcode": "BA2 3AP",
                "ParentODSCode": "V001",
                "ParentName": "Fake Parent",
                "Phone": "01234566544",
                "Email": "fakemail@gmail.com",
                "Website": "www.faketeeth.com"
            },
            {
                "OrganisationID": 222,
                "OrganisationCode": "V001112",
                "OrganisationType": "Dentists",
                "SubType": "UNKNOWN",
                "OrganisationStatus": "Visible",
                "OrganisationName": "Fake Dentist 2",
                "Address1": "1 Fake Street",
                "Address2": "",
                "Address3": "",
                "City": "Fake Town",
                "County": "Fake County",
                "Postcode": "BA2 3AP",
                "ParentODSCode": "V001",
                "ParentName": "Fake Parent",
                "Phone": "01234566544",
                "Email": "fakemail@gmail.com",
                "Website": "www.faketeeth.com"
            }
        ],
        [
            {
                "OrganisationId": 111,
                "WeekDay": "Monday",
                "Times": "08:00-16:00",
                "IsOpen": "True",
                "OpeningTimeType": "General",
                "AdditonalOpeningDate": ""
            },
            {
                "OrganisationId": 111,
                "WeekDay": "Tuesday",
                "Times": "08:00-16:00",
                "IsOpen": "True",
                "OpeningTimeType": "General",
                "AdditonalOpeningDate": ""
            },
            {
                "OrganisationId": 111,
                "WeekDay": "",
                "Times": "08:00-16:00",
                "IsOpen": "True",
                "OpeningTimeType": "Additional",
                "AdditonalOpeningDate": "May 3 2022"
            },
            {
                "OrganisationId": 111,
                "WeekDay": "",
                "Times": "09:00-16:00",
                "IsOpen": "True",
                "OpeningTimeType": "Additional",
                "AdditonalOpeningDate": "May 8 2022"
            },
            {
                "OrganisationId": 222,
                "WeekDay": "",
                "Times": "",
                "IsOpen": "False",
                "OpeningTimeType": "Additional",
                "AdditonalOpeningDate": "May 8 2022"
            },
            {
                "OrganisationId": 222,
                "WeekDay": "Friday",
                "Times": "09:00-19:00",
                "IsOpen": "True",
                "OpeningTimeType": "General",
                "AdditonalOpeningDate": ""
            },
        ]
    ]

    std1 = StandardOpeningTimes()
    std1.monday.append(OP("08:00-16:00"))
    std1.tuesday.append(OP("08:00-16:00"))
    spec1 = [
        SpecifiedOpeningTime([OP("08:00-16:00")], date(2022, 5, 3)),
        SpecifiedOpeningTime([OP("09:00-16:00")], date(2022, 5, 8))
    ]

    std2 = StandardOpeningTimes()
    std2.friday.append(OP("09:00-19:00"))
    spec2 = [
        SpecifiedOpeningTime([], date(2022, 5, 8), is_open=False)
    ]

    actual_dentists = get_dentists()

    d1 = actual_dentists[0]
    assert d1.odscode == "V001111"
    assert d1.postcode == "BA2 3AP"
    assert d1.standard_opening_times == std1
    assert SpecifiedOpeningTime.equal_lists(d1.specified_opening_times, spec1)

    d2 = actual_dentists[1]
    assert d2.odscode == "V001112"
    assert d2.org_name == "Fake Dentist 2"
    assert d2.standard_opening_times == std2
    assert SpecifiedOpeningTime.equal_lists(d2.specified_opening_times, spec2)
