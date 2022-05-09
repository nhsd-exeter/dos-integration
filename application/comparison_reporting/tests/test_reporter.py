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
            "DoS service ID",
            "DoS service UID",
            "DoS service Postcode",
            "DoS service Status"
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
            "DoS Service ODSCode",
            "DoS Service UID",
            "NHSUK Postcode",
            "DoS Service Postcode"
        ],
        data=[
            [nhs1.odscode, dos1b.odscode, dos1b.uid, nhs1.postcode, dos1b.postcode],
            [nhs2.odscode, dos2b.odscode, dos2b.uid, nhs2.postcode, dos2b.postcode],
            [nhs3.odscode, dos3b.odscode, dos3b.uid, nhs3.postcode, dos3b.postcode]
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
    std1.add_open_period(op3, "wedesday")

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
    dos3b = dummy_dos_service(odscode="QR334", typeid=PHARMACY_TYPE_ID)
    dos3b._standard_opening_times = std1

    nhs_entities = [nhs1, nhs2, nhs3]
    dos_services = [dos1a, dos1b, dos2a, dos2b, dos3a, dos3b]
    reporter = Reporter(nhs_entities, dos_services)
    pc_report = reporter.create_std_opening_times_comparison_report()

    expected_pc_report = DataFrame(
        columns=[
            "NHSUK ODSCode",
            "DoS Service ODSCode",
            "DoS Service UID",
            "NHSUK Standard Opening Times",
            "DoS Standard Opening Times"
        ],
        data=[
            [
                nhs1.odscode,
                dos1b.odscode,
                dos1b.uid,
                nhs1.standard_opening_times.to_string("\n"),
                dos1b._standard_opening_times.to_string("\n")
            ],
            [
                nhs2.odscode,
                dos2b.odscode,
                dos2b.uid,
                nhs2.standard_opening_times.to_string("\n"),
                dos2b._standard_opening_times.to_string("\n")
            ],
            [
                nhs3.odscode,
                dos3b.odscode,
                dos3b.uid,
                nhs3.standard_opening_times.to_string("\n"),
                dos3b._standard_opening_times.to_string("\n")
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

    nhs_entities = [nhs1, nhs2, nhs3]
    reporter = Reporter(nhs_entities, [])
    pc_report = reporter.create_invalid_std_opening_times_report()

    expected_pc_report = DataFrame(
        columns=[
            "NHSUK ODSCode",
            "NHSUK Org Name",
            "NHSUK Standard Opening Times"
        ],
        data=[
            [
                nhs2.odscode,
                nhs2.org_name,
                nhs2.standard_opening_times.to_string("\n")
            ],
            [
                nhs3.odscode,
                nhs3.org_name,
                nhs3.standard_opening_times.to_string("\n")
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

    dos1a = dummy_dos_service(odscode="FAT91", typeid=PHARMACY_TYPE_ID)
    dos1a._specified_opening_times = [spec1, spec2]
    dos1b = dummy_dos_service(odscode="FAT91", typeid=PHARMACY_TYPE_ID)
    dos1b._specified_opening_times = [spec2, spec3]
    dos2a = dummy_dos_service(odscode="GH291", typeid=PHARMACY_TYPE_ID)
    dos2a._specified_opening_times = [spec2, spec4]
    dos2b = dummy_dos_service(odscode="GH291", typeid=PHARMACY_TYPE_ID)
    dos2b._specified_opening_times = [spec1, spec2]
    dos3a = dummy_dos_service(odscode="QR334", typeid=PHARMACY_TYPE_ID)
    dos3a._specified_opening_times = [spec2, spec3]
    dos3b = dummy_dos_service(odscode="QR334", typeid=PHARMACY_TYPE_ID)
    dos3b._specified_opening_times = [spec1, spec2]

    nhs_entities = [nhs1, nhs2, nhs3]
    dos_services = [dos1a, dos1b, dos2a, dos2b, dos3a, dos3b]
    reporter = Reporter(nhs_entities, dos_services)
    pc_report = reporter.create_spec_opening_times_comparison_report()

    expected_pc_report = DataFrame(
        columns=[
            "NHSUK ODSCode",
            "DoS Service ODSCode",
            "DoS Service UID",
            "NHSUK Specified Opening Times",
            "DoS Specified Opening Times"
        ],
        data=[
            [
                nhs1.odscode,
                dos1b.odscode,
                dos1b.uid,
                "\n".join(str(sot) for sot in nhs1.specified_opening_times),
                "\n".join(str(sot) for sot in dos1b._specified_opening_times)
            ],
            [
                nhs2.odscode,
                dos2b.odscode,
                dos2b.uid,
                "\n".join(str(sot) for sot in nhs2.specified_opening_times),
                "\n".join(str(sot) for sot in dos3b._specified_opening_times)
            ],
            [
                nhs3.odscode,
                dos3b.odscode,
                dos3b.uid,
                "\n".join(str(sot) for sot in nhs3.specified_opening_times),
                "\n".join(str(sot) for sot in dos3b._specified_opening_times)
            ]
        ])

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

    nhs_entities = [nhs1, nhs2, nhs3]
    reporter = Reporter(nhs_entities, [])
    pc_report = reporter.create_invalid_spec_opening_times_report()

    expected_pc_report = DataFrame(
        columns=[
            "NHSUK ODSCode",
            "NHSUK Org Name",
            "NHSUK Specified Opening Times"
        ],
        data=[
            [
                nhs2.odscode,
                nhs2.org_name,
                "\n".join(str(sot) for sot in nhs2.specified_opening_times)
            ],
            [
                nhs3.odscode,
                nhs3.org_name,
                "\n".join(str(sot) for sot in nhs3.specified_opening_times)
            ]
        ])

    assert_frame_equal(expected_pc_report, pc_report)
