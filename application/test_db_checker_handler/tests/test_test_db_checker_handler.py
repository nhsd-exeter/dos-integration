from dataclasses import dataclass
from json import dumps
from unittest.mock import MagicMock, patch

from pytest import fixture, raises

from ..test_db_checker_handler import lambda_handler

FILE_PATH = "application.test_db_checker_handler.test_db_checker_handler"


@fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = "eventbridge-dlq-handler"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:eventbridge-dlq-handler"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()


@patch(f"{FILE_PATH}.query_dos_db")
def test_type_ods(query_dos_mock, lambda_context):
    # Arrange
    mock_connection = MagicMock()
    query_dos_mock.return_value = mock_connection
    mock_connection.fetchall.return_value = [("ODS12"), ("ODS11")]

    test_input = {"type": "get_odscodes"}

    # Act
    response = lambda_handler(test_input, lambda_context)
    # Assert
    query_dos_mock.assert_called_once_with(
        "SELECT LEFT(odscode, 5) FROM services WHERE typeid IN (131, 132, 134, 137, 13) "
        "AND statusid = '1' AND odscode IS NOT NULL",
        None,
    )
    assert response == '["ODS12", "ODS11"]'


@patch(f"{FILE_PATH}.query_dos_db")
def test_type_change_with_id(query_dos_mock, lambda_context):
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
    mock_connection = MagicMock()
    query_dos_mock.return_value = mock_connection
    mock_connection.fetchall.return_value = [(dumps(expected))]

    test_input = {"type": "get_changes", "correlation_id": "dave"}

    # Act
    response = lambda_handler(test_input, lambda_context)
    # Assert
    query_dos_mock.assert_called_once_with("SELECT value from changes where externalref = 'dave'", None)
    bla = dumps(dumps(expected))
    assert response == f"[{bla}]"


@patch(f"{FILE_PATH}.query_dos_db")
def test_type_change_no_id(query_dos_mock, lambda_context):
    # Arrange
    test_input = {"type": "get_changes"}
    # Act
    with raises(ValueError) as err:
        lambda_handler(test_input, lambda_context)
    # Assert
    assert str(err.value) == "Missing correlation id"
    query_dos_mock.assert_not_called()


@patch(f"{FILE_PATH}.get_matching_dos_services")
def test_get_demographics_no_match(matching_dos_mock, lambda_context):
    # Arrange
    test_input = {"type": "change_event_demographics", "odscode": "FA100"}
    matching_dos_mock.return_value = []
    with raises(ValueError) as err:
        lambda_handler(test_input, lambda_context)
    # Assert
    matching_dos_mock.assert_called_once_with("FA100")
    assert str(err.value) == "No matching services for ods FA100"

@patch(f"{FILE_PATH}.get_matching_dos_services")
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
