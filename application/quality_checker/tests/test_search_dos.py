from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock, patch

from application.quality_checker.search_dos import (
    search_for_incorrectly_profiled_z_code_on_correct_type,
    search_for_incorrectly_profiled_z_code_on_incorrect_type,
    search_for_matching_services,
    search_for_pharmacy_ods_codes,
)
from common.commissioned_service_type import BLOOD_PRESSURE, PALLIATIVE_CARE
from common.constants import DOS_ACTIVE_STATUS_ID, PHARMACY_SERVICE_TYPE_IDS
from common.dos import DoSService

FILE_PATH = "application.quality_checker.search_dos"


@patch(f"{FILE_PATH}.query_dos_db")
def test_search_for_pharmacy_ods_codes(mock_query_dos_db: MagicMock) -> None:
    # Arrange
    connection = MagicMock()
    odscode = "ABC123"
    mock_query_dos_db.return_value.fetchall.return_value = [{"left": odscode}]
    # Act
    response = search_for_pharmacy_ods_codes(connection)
    # Assert
    assert response == {odscode}
    mock_query_dos_db.assert_called_once_with(
        connection,
        "SELECT LEFT(odscode, 5) FROM services s WHERE s.typeid = ANY(%(PHARMACY_SERVICE_TYPE_IDS)s) "
        "AND s.statusid = %(ACTIVE_STATUS_ID)s AND LEFT(REPLACE(TRIM(odscode), CHR(9), ''), 1) IN ('F', 'f')",
        {"PHARMACY_SERVICE_TYPE_IDS": PHARMACY_SERVICE_TYPE_IDS, "ACTIVE_STATUS_ID": DOS_ACTIVE_STATUS_ID},
    )


def get_service_data() -> dict[str, Any]:
    return {
        "id": 9999,
        "uid": "159514725",
        "name": "fake name",
        "odscode": "FA9321",
        "address": "80 Street$Town",
        "town": "Town",
        "postcode": "TES T12",
        "web": None,
        "email": None,
        "fax": None,
        "nonpublicphone": None,
        "typeid": 13,
        "parentid": 123486,
        "subregionid": 21813557,
        "statusid": 1,
        "createdtime": datetime(2011, 8, 24, 9, 17, 24, tzinfo=UTC),
        "modifiedtime": datetime(2019, 3, 13, 0, 37, 7, tzinfo=UTC),
        "publicphone": "0123 012 012",
        "publicname": None,
        "service_type_name": "my service",
        "status_name": "Active",
        "easting": "123456",
        "northing": "123456",
        "latitude": "123456",
        "longitude": "123456",
    }


@patch(f"{FILE_PATH}.query_dos_db")
def test_search_for_matching_services(mock_query_dos_db: MagicMock) -> None:
    # Arrange
    connection = MagicMock()
    odscode = "ABC12"
    service = get_service_data()
    dos_service = DoSService(service)
    mock_query_dos_db.return_value.fetchall.return_value = [service]
    # Act
    response = search_for_matching_services(connection, odscode)
    # Assert
    assert response == [dos_service]
    mock_query_dos_db.assert_called_once_with(
        connection,
        "SELECT s.id, uid, s.name, odscode, address, postcode, web, typeid,statusid, ss.name status_name, publicphone, "
        "publicname, st.name service_type_name FROM services s LEFT JOIN servicetypes st ON s.typeid = st.id LEFT JOIN "
        "servicestatuses ss on s.statusid = ss.id WHERE s.odscode LIKE %(ODSCODE)s AND s.statusid = "
        "%(ACTIVE_STATUS_ID)s AND s.typeid = ANY(%(PHARMACY_SERVICE_TYPE_IDS)s)",
        {
            "ODSCODE": f"{odscode}%",
            "ACTIVE_STATUS_ID": DOS_ACTIVE_STATUS_ID,
            "PHARMACY_SERVICE_TYPE_IDS": PHARMACY_SERVICE_TYPE_IDS,
        },
    )


@patch(f"{FILE_PATH}.query_dos_db")
def test_search_for_incorrectly_profiled_z_code_on_incorrect_type(mock_query_dos_db: MagicMock) -> None:
    # Arrange
    connection = MagicMock()
    service = get_service_data()
    dos_service = DoSService(service)
    mock_query_dos_db.return_value.fetchall.return_value = [service]
    # Act
    response = search_for_incorrectly_profiled_z_code_on_incorrect_type(connection, BLOOD_PRESSURE)
    # Assert
    assert response == [dos_service]
    mock_query_dos_db.assert_called_once_with(
        connection,
        "SELECT s.id, uid, s.name, odscode, address, postcode, web, typeid, statusid, ss.name status_name, "
        "publicphone, publicname, st.name service_type_name "
        "FROM services s LEFT JOIN servicetypes st ON s.typeid = st.id "
        "LEFT JOIN servicestatuses ss on s.statusid = ss.id "
        "LEFT JOIN servicesgsds sgsds on s.id = sgsds.serviceid "
        "WHERE sgsds.sgid = %(SYMPTOM_GROUP)s AND sgsds.sdid = %(SYMPTOM_DISCRIMINATOR)s "
        "AND s.statusid = %(ACTIVE_STATUS_ID)s AND s.typeid = ANY(%(SERVICE_TYPE_IDS)s) "
        "AND LEFT(s.odscode,1) in ('F', 'f')",
        {
            "ACTIVE_STATUS_ID": DOS_ACTIVE_STATUS_ID,
            "SERVICE_TYPE_IDS": [13, 131, 132, 134, 137, 149],
            "SYMPTOM_GROUP": BLOOD_PRESSURE.DOS_SYMPTOM_GROUP,
            "SYMPTOM_DISCRIMINATOR": BLOOD_PRESSURE.DOS_SYMPTOM_DISCRIMINATOR,
        },
    )


@patch(f"{FILE_PATH}.query_dos_db")
def test_search_for_incorrectly_profiled_z_code_on_correct_type(mock_query_dos_db: MagicMock) -> None:
    # Arrange
    connection = MagicMock()
    service = get_service_data()
    dos_service = DoSService(service)
    mock_query_dos_db.return_value.fetchall.return_value = [service]
    # Act
    response = search_for_incorrectly_profiled_z_code_on_correct_type(connection, PALLIATIVE_CARE)
    # Assert
    assert response == [dos_service]
    mock_query_dos_db.assert_called_once_with(
        connection,
        "SELECT s.id, uid, s.name, odscode, address, postcode, web, typeid, statusid, ss.name status_name, "
        "publicphone, publicname, st.name service_type_name "
        "FROM services s LEFT JOIN servicetypes st ON s.typeid = st.id "
        "LEFT JOIN servicestatuses ss on s.statusid = ss.id "
        "LEFT JOIN servicesgsds sgsds on s.id = sgsds.serviceid "
        "WHERE sgsds.sgid = %(SYMPTOM_GROUP)s AND sgsds.sdid = %(SYMPTOM_DISCRIMINATOR)s "
        "AND s.statusid = %(ACTIVE_STATUS_ID)s AND s.typeid = ANY(%(SERVICE_TYPE_IDS)s) "
        "AND LEFT(s.odscode,1) in ('F', 'f') AND LENGTH(s.odscode) > 5",
        {
            "ACTIVE_STATUS_ID": DOS_ACTIVE_STATUS_ID,
            "SERVICE_TYPE_IDS": [13],
            "SYMPTOM_GROUP": PALLIATIVE_CARE.DOS_SYMPTOM_GROUP,
            "SYMPTOM_DISCRIMINATOR": PALLIATIVE_CARE.DOS_SYMPTOM_DISCRIMINATOR,
        },
    )
