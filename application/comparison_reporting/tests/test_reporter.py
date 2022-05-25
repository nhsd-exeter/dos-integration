from unittest.mock import patch
from datetime import date

from pandas import DataFrame
from pandas.testing import assert_frame_equal

from common.tests.conftest import dummy_dos_service
from common.nhs import NHSEntity
from common.opening_times import StandardOpeningTimes, SpecifiedOpeningTime, OpenPeriod
from common.constants import PHARMACY_SERVICE_TYPE_IDS, DENTIST_SERVICE_TYPE_IDS

PHARMACY_TYPE_ID = PHARMACY_SERVICE_TYPE_IDS[0]
DENTIST_TYPE_ID = DENTIST_SERVICE_TYPE_IDS[0]
OP = OpenPeriod.from_string


@patch("common.dos.get_all_valid_dos_postcodes")
def test_create_invalid_postcode_report(mock_get_all_valid_dos_postcodes):
    from comparison_reporting.reporter import Reporter

    test_valid_postcodes = set(pc.replace(" ", "").upper() for pc in [
        "BA2 7EB",
        "TE57ER",
        "QR8 9PM",
        "R3 7YX"
    ])
    mock_get_all_valid_dos_postcodes.return_value = test_valid_postcodes

    nhs1 = NHSEntity({
        "ODSCode": "FAT911",
        "OrganisationName": "Fakey Mcfakename",
        "Postcode": "TE57EH"
    })
    nhs2 = NHSEntity({
        "ODSCode": "QR132",
        "OrganisationName": "Fakey Mcfakename 2",
        "Postcode": "BA27EB"
    })
    nhs3 = NHSEntity({
        "ODSCode": "TR272",
        "OrganisationName": "Fakey Mcfakename 3",
        "Postcode": "R3 7YX"
    })

    dos1 = dummy_dos_service(odscode="FAT91111", typeid=PHARMACY_TYPE_ID)

    nhs_entities = [nhs1, nhs2, nhs3]
    dos_services = [dos1]
    reporter = Reporter(nhs_entities, dos_services)

    pc_report = reporter.create_invalid_postcode_report()
    expected_pc_report = DataFrame(
        columns=[
            "NHSUK ODSCode",
            "NHSUK Organisation Name",
            "NHSUK Invalid Postcode",
            "DoS Service ID",
            "DoS Service UID",
            "DoS Service Postcode",
            "DoS Service Status"
        ],
        data=[
            [nhs1.odscode, nhs1.org_name, nhs1.postcode, dos1.id, dos1.uid, dos1.postcode, dos1.statusid]
        ])

    assert_frame_equal(expected_pc_report, pc_report)


def test_create_postcode_comparison_report():
    from comparison_reporting.reporter import Reporter

    nhs1 = NHSEntity({
        "ODSCode": "FAT91",
        "OrganisationName": "Fakey Mcfakename",
        "Postcode": "TE57EH"
    })
    nhs2 = NHSEntity({
        "ODSCode": "QR132",
        "OrganisationName": "Fakey Mcfakename 2",
        "Postcode": "BA27EB"
    })
    nhs3 = NHSEntity({
        "ODSCode": "V3272456",
        "OrganisationName": "Fakey Mcfakename 3",
        "Postcode": "R3 7YX"
    })

    dos1a = dummy_dos_service(odscode="FAT911a", postcode="TE57EH", typeid=PHARMACY_TYPE_ID)
    dos1b = dummy_dos_service(odscode="FAT911b", postcode="TE57EW", typeid=PHARMACY_TYPE_ID)
    dos2a = dummy_dos_service(odscode="QR132a", postcode="BA27EB", typeid=PHARMACY_TYPE_ID)
    dos2b = dummy_dos_service(odscode="QR132b", postcode="KA27EB", typeid=PHARMACY_TYPE_ID)
    dos3a = dummy_dos_service(odscode="V3272456a", postcode="R3 7YX", typeid=PHARMACY_TYPE_ID)
    dos3b = dummy_dos_service(odscode="V3272456b", postcode="R3 7YY", typeid=PHARMACY_TYPE_ID)

    nhs_entities = [nhs1, nhs2, nhs3]
    dos_services = [dos1a, dos1b, dos2a, dos2b, dos3a, dos3b]
    reporter = Reporter(nhs_entities, dos_services)
    pc_report = reporter.create_postcode_comparison_report()

    expected_pc_report = DataFrame(
        columns=[
            "NHSUK ODSCode",
            "NHSUK Name",
            "NHSUK Postcode",
            "DoS Service ODSCode",
            "DoS Service UID",
            "DoS Service Name",
            "DoS Service Postcode",
            "DoS Service Status"
        ],
        data=[
            [
                nhs1.odscode,
                nhs1.org_name,
                nhs1.postcode,
                dos1b.odscode,
                dos1b.uid,
                dos1b.name,
                dos1b.postcode,
                dos1b.statusid
            ],
            [
                nhs2.odscode,
                nhs2.org_name,
                nhs2.postcode,
                dos2b.odscode,
                dos2b.uid,
                dos2b.name,
                dos2b.postcode,
                dos2b.statusid
            ],
            [
                nhs3.odscode,
                nhs3.org_name,
                nhs3.postcode,
                dos3b.odscode,
                dos3b.uid,
                dos3b.name,
                dos3b.postcode,
                dos3b.statusid
            ]
        ])

    assert_frame_equal(expected_pc_report, pc_report)


def test_create_std_opening_times_comparison_report():
    from comparison_reporting.reporter import Reporter

    op1 = OP("08:00-12:00")
    op2 = OP("03:00-18:00")
    op3 = OP("08:00-18:00")
    op4 = OP("07:00-10:00")

    std1 = StandardOpeningTimes()
    std1.add_open_period(op1, "monday")
    std1.add_open_period(op2, "tuesday")
    std1.add_open_period(op3, "wednesday")

    std2 = StandardOpeningTimes()
    std2.add_open_period(op2, "wednesday")
    std2.add_open_period(op2, "friday")
    std2.add_open_period(op4, "thursday")

    std3 = StandardOpeningTimes()
    std3.add_open_period(op3, "monday")
    std3.add_open_period(op3, "tuesday")
    std3.add_open_period(op3, "saturday")

    nhs1 = NHSEntity({"ODSCode": "FAT91"})
    nhs1.standard_opening_times = std1
    nhs2 = NHSEntity({"ODSCode": "GH291"})
    nhs2.standard_opening_times = std2
    nhs3 = NHSEntity({"ODSCode": "QR334"})
    nhs3.standard_opening_times = std3

    dos1a = dummy_dos_service(odscode="FAT91", typeid=PHARMACY_TYPE_ID)
    dos1a._standard_opening_times = std1
    dos1b = dummy_dos_service(odscode="FAT91", typeid=PHARMACY_TYPE_ID)
    dos1b._standard_opening_times = std3
    dos2a = dummy_dos_service(odscode="GH291", typeid=PHARMACY_TYPE_ID)
    dos2a._standard_opening_times = std2
    dos2b = dummy_dos_service(odscode="GH291", typeid=PHARMACY_TYPE_ID)
    dos2b._standard_opening_times = std1
    dos3a = dummy_dos_service(odscode="QR334", typeid=PHARMACY_TYPE_ID)
    dos3a._standard_opening_times = std3

    nhs_entities = [nhs1, nhs2, nhs3]
    dos_services = [dos1a, dos1b, dos2a, dos2b, dos3a]
    reporter = Reporter(nhs_entities, dos_services)
    pc_report = reporter.create_std_opening_times_comparison_report()

    expected_pc_report = DataFrame(
        columns=[
            "NHSUK ODSCode",
            "NHSUK Standard Opening Times",
            "Weekday",
            "DoS Service ODSCode",
            "DoS Service UID",
            "DoS Service Name",
            "DoS Standard Opening Times",
            "DoS Service Status"
        ],
        data=[
            [
                nhs1.odscode,
                OpenPeriod.list_string(nhs1.standard_opening_times.get_openings("monday")),
                "monday",
                dos1b.odscode,
                dos1b.uid,
                dos1b.name,
                OpenPeriod.list_string(dos1b._standard_opening_times.get_openings("monday")),
                dos1b.statusid
            ],
            [
                nhs1.odscode,
                OpenPeriod.list_string(nhs1.standard_opening_times.get_openings("tuesday")),
                "tuesday",
                dos1b.odscode,
                dos1b.uid,
                dos1b.name,
                OpenPeriod.list_string(dos1b._standard_opening_times.get_openings("tuesday")),
                dos1b.statusid
            ],
            [
                nhs1.odscode,
                OpenPeriod.list_string(nhs1.standard_opening_times.get_openings("wednesday")),
                "wednesday",
                dos1b.odscode,
                dos1b.uid,
                dos1b.name,
                OpenPeriod.list_string(dos1b._standard_opening_times.get_openings("wednesday")),
                dos1b.statusid
            ],
            [
                nhs1.odscode,
                OpenPeriod.list_string(nhs1.standard_opening_times.get_openings("saturday")),
                "saturday",
                dos1b.odscode,
                dos1b.uid,
                dos1b.name,
                OpenPeriod.list_string(dos1b._standard_opening_times.get_openings("saturday")),
                dos1b.statusid
            ],
            [
                nhs2.odscode,
                OpenPeriod.list_string(nhs2.standard_opening_times.get_openings("monday")),
                "monday",
                dos2b.odscode,
                dos2b.uid,
                dos2b.name,
                OpenPeriod.list_string(dos2b._standard_opening_times.get_openings("monday")),
                dos2b.statusid
            ],
            [
                nhs2.odscode,
                OpenPeriod.list_string(nhs2.standard_opening_times.get_openings("tuesday")),
                "tuesday",
                dos2b.odscode,
                dos2b.uid,
                dos2b.name,
                OpenPeriod.list_string(dos2b._standard_opening_times.get_openings("tuesday")),
                dos2b.statusid
            ],
            [
                nhs2.odscode,
                OpenPeriod.list_string(nhs2.standard_opening_times.get_openings("wednesday")),
                "wednesday",
                dos2b.odscode,
                dos2b.uid,
                dos2b.name,
                OpenPeriod.list_string(dos2b._standard_opening_times.get_openings("wednesday")),
                dos2b.statusid
            ],
            [
                nhs2.odscode,
                OpenPeriod.list_string(nhs2.standard_opening_times.get_openings("thursday")),
                "thursday",
                dos2b.odscode,
                dos2b.uid,
                dos2b.name,
                OpenPeriod.list_string(dos2b._standard_opening_times.get_openings("thursday")),
                dos2b.statusid
            ],
            [
                nhs2.odscode,
                OpenPeriod.list_string(nhs2.standard_opening_times.get_openings("friday")),
                "friday",
                dos2b.odscode,
                dos2b.uid,
                dos2b.name,
                OpenPeriod.list_string(dos2b._standard_opening_times.get_openings("friday")),
                dos2b.statusid
            ]
        ])

    assert_frame_equal(expected_pc_report, pc_report)


def test_create_invalid_std_opening_times_report():
    from comparison_reporting.reporter import Reporter

    op1 = OP("08:00-12:00")
    op2 = OP("13:00-18:00")
    op3 = OP("08:00-18:00")
    op4 = OP("07:00-10:00")

    std1 = StandardOpeningTimes()
    std1.add_open_period(op1, "monday")
    std1.add_open_period(op2, "tuesday")
    std1.add_open_period(op3, "wedesday")

    std2 = StandardOpeningTimes()
    std2.add_open_period(op2, "wednesday")
    std2.add_open_period(op2, "friday")
    std2.add_open_period(op3, "friday")
    std2.add_open_period(op4, "thursday")

    std3 = StandardOpeningTimes()
    std3.add_open_period(op3, "monday")
    std3.add_open_period(op4, "monday")
    std3.add_open_period(op3, "tuesday")
    std3.add_open_period(op3, "saturday")

    nhs1 = NHSEntity({"ODSCode": "FAT91", "OrganisationName": "org 1"})
    nhs1.standard_opening_times = std1
    nhs2 = NHSEntity({"ODSCode": "GH291", "OrganisationName": "org 2"})
    nhs2.standard_opening_times = std2
    nhs3 = NHSEntity({"ODSCode": "QR334", "OrganisationName": "org 3"})
    nhs3.standard_opening_times = std3

    dos2 = dummy_dos_service(odscode="GH29111", typeid=PHARMACY_TYPE_ID)

    nhs_entities = [nhs1, nhs2, nhs3]
    dos_services = [dos2]
    reporter = Reporter(nhs_entities, dos_services)
    pc_report = reporter.create_invalid_std_opening_times_report()

    expected_pc_report = DataFrame(
        columns=[
            "NHSUK ODSCode",
            "NHSUK Org Name",
            "NHSUK Standard Opening Times",
            "DoS Service ID",
            "DoS Service UID",
            "DoS Service Name",
            "DoS Service Status"
        ],
        data=[
            [
                nhs2.odscode,
                nhs2.org_name,
                nhs2.standard_opening_times.to_string("\n"),
                dos2.id,
                dos2.uid,
                dos2.name,
                dos2.statusid
            ],
            [
                nhs3.odscode,
                nhs3.org_name,
                nhs3.standard_opening_times.to_string("\n"),
                "",
                "",
                "",
                ""
            ],
        ])

    assert_frame_equal(expected_pc_report, pc_report)


def test_create_spec_opening_times_comparison_report():
    from comparison_reporting.reporter import Reporter

    op1 = OP("08:00-12:00")
    op2 = OP("13:00-18:00")
    op3 = OP("08:00-18:00")
    op4 = OP("07:00-10:00")

    spec1 = SpecifiedOpeningTime([op1, op2], date(2021, 9, 1), is_open=True)
    spec2 = SpecifiedOpeningTime([op3], date(2021, 9, 12), is_open=True)
    spec3 = SpecifiedOpeningTime([op4], date(2021, 10, 3), is_open=True)
    spec4 = SpecifiedOpeningTime([], date(2021, 3, 25), is_open=False)

    nhs1 = NHSEntity({"ODSCode": "FAT91"})
    nhs1.specified_opening_times = [spec1, spec2]

    nhs2 = NHSEntity({"ODSCode": "GH291"})
    nhs2.specified_opening_times = [spec2, spec4]

    nhs3 = NHSEntity({"ODSCode": "QR334"})
    nhs3.specified_opening_times = [spec2, spec3]

    dos1a = dummy_dos_service(odscode="FAT91a", typeid=PHARMACY_TYPE_ID)
    dos1a._specified_opening_times = [spec1, spec2]
    dos1b = dummy_dos_service(odscode="FAT91b", typeid=PHARMACY_TYPE_ID)
    dos1b._specified_opening_times = [spec2, spec3]
    dos2a = dummy_dos_service(odscode="GH291a", typeid=PHARMACY_TYPE_ID)
    dos2a._specified_opening_times = [spec2, spec4]

    dos2b = dummy_dos_service(odscode="GH291b", typeid=PHARMACY_TYPE_ID)
    dos2b._specified_opening_times = [spec1, spec2]

    dos3a = dummy_dos_service(odscode="QR334a", typeid=PHARMACY_TYPE_ID)
    dos3a._specified_opening_times = [spec2, spec3]

    nhs_entities = [nhs1, nhs2, nhs3]
    dos_services = [dos1a, dos1b, dos2a, dos2b, dos3a]
    reporter = Reporter(nhs_entities, dos_services)
    pc_report = reporter.create_spec_opening_times_comparison_report()

    expected_pc_report = DataFrame(
        columns=[
            "NHSUK ODSCode",
            "NHSUK Specified Opening Times",
            "Date",
            "DoS Service ODSCode",
            "DoS Service UID",
            "DoS Service Name",
            "DoS Specified Opening Times",
            "DoS Service Status"
        ],
        data=[
            [
                nhs1.odscode,
                "[08:00:00-12:00:00, 13:00:00-18:00:00]",
                "2021-09-01",
                dos1b.odscode,
                dos1b.uid,
                dos1b.name,
                "NULL",
                dos1b.statusid
            ],
            [
                nhs1.odscode,
                "NULL",
                "2021-10-03",
                dos1b.odscode,
                dos1b.uid,
                dos1b.name,
                "[07:00:00-10:00:00]",
                dos1b.statusid
            ],

            [
                nhs2.odscode,
                "[]",
                "2021-03-25",
                dos2b.odscode,
                dos2b.uid,
                dos2b.name,
                "NULL",
                dos2b.statusid
            ],
            [
                nhs2.odscode,
                "NULL",
                "2021-09-01",
                dos2b.odscode,
                dos2b.uid,
                dos2b.name,
                "[08:00:00-12:00:00, 13:00:00-18:00:00]",
                dos2b.statusid
            ]
        ])

    expected_pc_report.sort_values(["NHSUK ODSCode", "Date"], inplace=True, ignore_index=True)
    pc_report.sort_values(["NHSUK ODSCode", "Date"], inplace=True, ignore_index=True)

    print(expected_pc_report.to_string(), "\n\n", pc_report.to_string())

    assert_frame_equal(expected_pc_report, pc_report)


def test_invalid_spec_opening_times_report():
    from comparison_reporting.reporter import Reporter

    op1 = OP("08:00-12:00")
    op2 = OP("13:00-18:00")
    op3 = OP("08:00-18:00")
    op4 = OP("07:00-10:00")

    spec1 = SpecifiedOpeningTime([op1, op2], date(2021, 9, 1), is_open=True)
    spec2 = SpecifiedOpeningTime([op3], date(2021, 9, 12), is_open=True)
    spec3 = SpecifiedOpeningTime([op4], date(2021, 10, 3), is_open=True)
    spec4 = SpecifiedOpeningTime([], date(2021, 3, 25), is_open=False)

    spec5 = SpecifiedOpeningTime([], date(2021, 9, 4), is_open=True)
    spec6 = SpecifiedOpeningTime([op1, op3], date(2021, 9, 4), is_open=True)

    nhs1 = NHSEntity({"ODSCode": "FAT91", "OrganisationName": "org 1"})
    nhs1.specified_opening_times = [spec1, spec2, spec3, spec4]
    nhs2 = NHSEntity({"ODSCode": "GH291", "OrganisationName": "org 2"})
    nhs2.specified_opening_times = [spec5, spec4]
    nhs3 = NHSEntity({"ODSCode": "QR334", "OrganisationName": "org 3"})
    nhs3.specified_opening_times = [spec2, spec6]

    dos2 = dummy_dos_service(odscode="GH29111", typeid=PHARMACY_TYPE_ID)

    nhs_entities = [nhs1, nhs2, nhs3]
    dos_services = [dos2]
    reporter = Reporter(nhs_entities, dos_services)
    pc_report = reporter.create_invalid_spec_opening_times_report()

    expected_pc_report = DataFrame(
        columns=[
            "NHSUK ODSCode",
            "NHSUK Org Name",
            "NHSUK Specified Opening Times",
            "DoS Service ID",
            "DoS Service UID",
            "DoS Service Name",
            "DoS Service Status"
        ],
        data=[
            [
                nhs2.odscode,
                nhs2.org_name,
                "\n".join(str(sot) for sot in nhs2.specified_opening_times),
                dos2.id,
                dos2.uid,
                dos2.name,
                dos2.statusid
            ],
            [
                nhs3.odscode,
                nhs3.org_name,
                "\n".join(str(sot) for sot in nhs3.specified_opening_times),
                "",
                "",
                "",
                ""
            ]
        ])

    assert_frame_equal(expected_pc_report, pc_report)
