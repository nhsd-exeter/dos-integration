from application.service_sync.dos_logger import DoSLogger
from logging import INFO
from pytest import CaptureFixture


def test_dos_logger():
    # Arrange
    correlation_id = "12345"
    service_uid = "12345"
    service_name = "Test Service"
    type_id = "1"
    # Act
    dos_logger = DoSLogger(
        correlation_id=correlation_id, service_uid=service_uid, service_name=service_name, type_id=type_id
    )
    # Assert
    assert dos_logger.logger.name == "dos_logger"
    assert dos_logger.logger.level == INFO
    assert (
        dos_logger.format
        == "%(asctime)s|%(levelname)s|DOS_INTEGRATION|%(service_uid)s|%(service_name)s|%(type_id)s|%(data_field_modified)s|%(action)s|%(data_changes)s|message=%(message)s|%(correlationId)s"  # noqa E501
    )
    assert dos_logger.correlation_id == correlation_id
    assert dos_logger.service_uid == service_uid
    assert dos_logger.service_name == service_name
    assert dos_logger.type_id == type_id


# TODO: Parameterise the tests for the log_demographics_service_update to take in different types
def test_dos_logger_log_demographics_service_update(capsys: CaptureFixture):
    # Arrange
    correlation_id = "123456"
    service_uid = "12345"
    service_name = "Test Service"
    type_id = "1"
    data_field_modified = "test_field"
    action = "update"
    previous_value = "test_value"
    new_value = "new_test_value"
    dos_logger = DoSLogger(
        correlation_id=correlation_id, service_uid=service_uid, service_name=service_name, type_id=type_id
    )
    # Act
    dos_logger.log_demographics_service_update(
        data_field_modified=data_field_modified, action=action, previous_value=previous_value, new_value=new_value
    )
    # Assert
    assert (
        f"|INFO|DOS_INTEGRATION|{service_uid}|{service_name}|{type_id}|{data_field_modified}|{action}|{previous_value}|{new_value}|message=ServiceUpdate|{correlation_id}"  # noqa E501
        in capsys.readouterr().err
    )
