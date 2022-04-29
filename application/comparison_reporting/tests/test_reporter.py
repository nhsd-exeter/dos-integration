from unittest.mock import patch

from pandas import DataFrame
from pandas.testing import assert_frame_equal

from common.tests.conftest import dummy_dos_service
from common.nhs import NHSEntity
from common.constants import PHARMACY_SERVICE_TYPE_IDS, DENTIST_SERVICE_TYPE_IDS

P_TYPE_ID = PHARMACY_SERVICE_TYPE_IDS[0]
D_TYPE_ID = DENTIST_SERVICE_TYPE_IDS[0]


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

    nhs_entities = [nhs1, nhs2, nhs3]
    dos_services = []
    reporter = Reporter(nhs_entities, dos_services)

    pc_report = reporter.create_invalid_postcode_report()
    expected_pc_report = DataFrame(
        columns=[
            "NHSUK ODSCode",
            "NHSUK Organisation Name",
            "NHSUK Invalid Postcode"
        ],
        data=[
            [nhs1.odscode, nhs1.org_name, nhs1.postcode]
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

    dos1a = dummy_dos_service(odscode="FAT911a", postcode="TE57EH", typeid=P_TYPE_ID)
    dos1b = dummy_dos_service(odscode="FAT911b", postcode="TE57EW", typeid=P_TYPE_ID)
    dos2a = dummy_dos_service(odscode="QR132a", postcode="BA27EB", typeid=P_TYPE_ID)
    dos2b = dummy_dos_service(odscode="QR132b", postcode="KA27EB", typeid=P_TYPE_ID)
    dos3a = dummy_dos_service(odscode="V3272456a", postcode="R3 7YX", typeid=D_TYPE_ID)
    dos3b = dummy_dos_service(odscode="V3272456b", postcode="R3 7YY", typeid=D_TYPE_ID)

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

    print(expected_pc_report)
    print(pc_report)

    assert_frame_equal(expected_pc_report, pc_report)
