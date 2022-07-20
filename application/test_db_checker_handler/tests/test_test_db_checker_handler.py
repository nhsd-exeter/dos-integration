from dataclasses import dataclass
from json import dumps
from unittest.mock import patch

from pytest import fixture, raises

from ..test_db_checker_handler import lambda_handler

FILE_PATH = "application.test_db_checker_handler.test_db_checker_handler"


@fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = "test_db_checker"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:test_db_checker-handler"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()


@patch(f"{FILE_PATH}.run_query")
def test_type_get_pharmacy_odscodes(mock_run_query, lambda_context):
    # Arrange
    mock_run_query.return_value = [("ODS12"), ("ODS11")]
    test_input = {"type": "get_pharmacy_odscodes"}
    # Act
    response = lambda_handler(test_input, lambda_context)
    # Assert
    mock_run_query.assert_called_once_with(
        "SELECT LEFT(odscode, 5) FROM services WHERE typeid IN (13, 131, 132, 134, 137) "
        "AND statusid = 1 AND odscode IS NOT NULL",
        None,
    )
    assert response == '["ODS12", "ODS11"]'


@patch(f"{FILE_PATH}.run_query")
def test_type_get_single_service_pharmacy_odscode(mock_run_query, lambda_context):
    # Arrange
    mock_run_query.return_value = [("ODS12"), ("ODS11")]
    test_input = {"type": "get_single_service_pharmacy_odscode"}
    # Act
    response = lambda_handler(test_input, lambda_context)
    # Assert
    mock_run_query.assert_called_once_with(
        "SELECT LEFT(odscode,5) FROM services WHERE typeid IN (13, 131, 132, 134, 137) "
        "AND statusid = 1 AND odscode IS NOT NULL AND RIGHT(address, 1) != '$' "
        "AND LENGTH(odscode) > 4 GROUP BY LEFT(odscode,5) HAVING COUNT(odscode) = 1",
        None,
    )
    assert response == '["ODS12", "ODS11"]'


@patch(f"{FILE_PATH}.run_query")
def test_type_get_services_count(mock_run_query, lambda_context):
    # Arrange
    mock_run_query.return_value = 2
    test_input = {"type": "get_services_count", "odscode": "ODS12"}
    # Act
    response = lambda_handler(test_input, lambda_context)
    # Assert
    mock_run_query.assert_called_once_with("SELECT count(*) from services where odscode like 'ODS12%'", None)
    assert response == "2"


@patch(f"{FILE_PATH}.run_query")
def test_type_get_pharmacy_odscodes_with_contacts(mock_run_query, lambda_context):
    # Arrange
    mock_run_query.return_value = [("ODS12"), ("ODS11")]
    test_input = {"type": "get_pharmacy_odscodes_with_contacts"}
    # Act
    response = lambda_handler(test_input, lambda_context)
    # Assert
    mock_run_query.assert_called_once_with(
        "SELECT LEFT(odscode,5) FROM services WHERE typeid IN (13, 131, 132, 134, 137) AND LENGTH(odscode) > 4 "
        "AND statusid = 1 AND odscode IS NOT NULL AND RIGHT(address, 1) != '$' "
        "AND publicphone IS NOT NULL AND web IS NOT NULL GROUP BY LEFT(odscode,5) HAVING COUNT(odscode) = 1",
        None,
    )
    assert response == '["ODS12", "ODS11"]'


@patch(f"{FILE_PATH}.run_query")
def test_type_get_dentist_odscodes(mock_run_query, lambda_context):
    # Arrange
    mock_run_query.return_value = [("ODS12"), ("ODS11")]
    test_input = {"type": "get_dentist_odscodes"}
    # Act
    response = lambda_handler(test_input, lambda_context)
    # Assert
    mock_run_query.assert_called_once_with(
        "SELECT odscode FROM services WHERE typeid = 12 "
        "AND statusid = 1 AND odscode IS NOT NULL AND LENGTH(odscode) = 6 AND LEFT(odscode, 1)='V'",
        None,
    )
    assert response == '["ODS12", "ODS11"]'


@patch(f"{FILE_PATH}.run_query")
def test_type_get_changes_with_id(mock_run_query, lambda_context):
    # Arrange
    expected = {
        "new": {
            "cmstelephoneno": {
                "changetype": "modify",
                "data": "0118 999 88199 9119 725 3",
                "area": "demographic",
                "previous": "0208 882 1081",
            }
        },
        "initiator": {"userid": "CHANGE_REQUEST", "timestamp": "2022-01-27 10:13:50"},
    }
    mock_run_query.return_value = expected

    test_input = {"type": "get_changes", "correlation_id": "dave"}
    # Act
    response = lambda_handler(test_input, lambda_context)
    # Assert
    mock_run_query.assert_called_once_with("SELECT value from changes where externalref = 'dave'", None)
    expected_output = dumps(expected)
    assert response == expected_output


@patch(f"{FILE_PATH}.run_query")
def test_type_get_changes_no_id(mock_run_query, lambda_context):
    # Arrange
    test_input = {"type": "get_changes"}
    # Act
    with raises(ValueError) as err:
        lambda_handler(test_input, lambda_context)
    # Assert
    assert str(err.value) == "Missing correlation id"
    mock_run_query.assert_not_called()


@patch(f"{FILE_PATH}.run_query")
def test_get_demographics_no_match(mock_run_query, lambda_context):
    # Arrange
    odscode = "FA100"
    test_input = {"type": "change_event_demographics", "odscode": odscode, "organisation_type_id": "PHA"}
    mock_run_query.return_value = []
    with raises(ValueError) as err:
        lambda_handler(test_input, lambda_context)
    # Assert
    mock_run_query.assert_called_once_with(
        "SELECT id, name, odscode, address, postcode, web, typeid, statusid, publicphone, "
        "publicname FROM services WHERE odscode like %(ODSCODE)s AND typeid IN (13, 131, 132, 134, 137) "
        "AND statusid = %(VALID_STATUS_ID)s AND odscode IS NOT NULL",
        {"ODSCODE": f"{odscode}%", "VALID_STATUS_ID": 1},
    )
    assert str(err.value) == f"No matching services for odscode {odscode}"


@patch(f"{FILE_PATH}.run_query")
def test_type_demographics(mock_run_query, lambda_context):
    # Arrange
    odscode = "FA100"
    expected = {
        "id": "1",
        "name": "Example",
        "odscode": "FA100",
        "address": "5-7 Kingsway$testown",
        "postcode": "BD16 4RP",
        "web": None,
        "typeid": 131,
        "statusid": 1,
        "publicphone": None,
        "publicname": None,
    }
    test_input = {"type": "change_event_demographics", "odscode": odscode, "organisation_type_id": "PHA"}
    mock_run_query.return_value = [list(expected.values())]
    # Act
    response = lambda_handler(test_input, lambda_context)
    # Assert
    mock_run_query.assert_called_once_with(
        "SELECT id, name, odscode, address, postcode, web, typeid, statusid, publicphone, "
        "publicname FROM services WHERE odscode like %(ODSCODE)s AND typeid IN (13, 131, 132, 134, 137) "
        "AND statusid = %(VALID_STATUS_ID)s AND odscode IS NOT NULL",
        {"ODSCODE": f"{odscode}%", "VALID_STATUS_ID": 1},
    )
    assert response == dumps(expected)


@patch(f"{FILE_PATH}.run_query")
def test_type_demographics_no_ods(matching_dos_mock, lambda_context):
    # Arrange
    test_input = {"type": "change_event_demographics"}
    # Act
    with raises(ValueError) as err:
        lambda_handler(test_input, lambda_context)
    # Assert
    assert str(err.value) == "Missing odscode"
    matching_dos_mock.assert_not_called()


@patch(f"{FILE_PATH}.get_standard_opening_times_from_db")
def test_type_standards_no_ods(mock_opening_times, lambda_context):
    # Arrange
    test_input = {"type": "change_event_standard_opening_times"}
    # Act
    with raises(ValueError) as err:
        lambda_handler(test_input, lambda_context)
    # Assert
    assert str(err.value) == "Missing service_id"
    mock_opening_times.assert_not_called()


@patch(f"{FILE_PATH}.get_specified_opening_times_from_db")
def test_type_specifieds_no_ods(mock_opening_times, lambda_context):
    # Arrange
    test_input = {"type": "change_event_specified_opening_times"}
    # Act
    with raises(ValueError) as err:
        lambda_handler(test_input, lambda_context)
    # Assert
    assert str(err.value) == "Missing service_id"
    mock_opening_times.assert_not_called()


@patch(f"{FILE_PATH}.query_dos_db")
def test_type_change_unknown_type(query_dos_mock, lambda_context):
    # Arrange
    test_input = {"type": "dave"}
    # Act
    with raises(ValueError) as err:
        lambda_handler(test_input, lambda_context)
    # Assert
    assert str(err.value) == "Unsupported request"
    query_dos_mock.assert_not_called()
