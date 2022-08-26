from logging import INFO
from os import environ

from pytest import CaptureFixture, fixture, mark

from application.service_sync.service_update_logging import ServiceUpdateLogger


SERVICE_UID = "12345"
SERVICE_NAME = "Test Service"
TYPE_ID = "1"


@fixture
def service_update_logger():
    yield ServiceUpdateLogger(service_uid=SERVICE_UID, service_name=SERVICE_NAME, type_id=TYPE_ID)


def test_dos_logger(service_update_logger: ServiceUpdateLogger):
    # Assert
    assert service_update_logger.logger.name == "service_undefined.application.service_sync.service_update_logging"
    assert service_update_logger.dos_logger.name == "dos_logger"
    assert service_update_logger.dos_logger.level == INFO
    assert service_update_logger.dos_format == (
        "%(asctime)s|%(levelname)s|DOS_INTEGRATION_%(environment)s|%(correlation_id)s|DOS_INTEGRATION|"
        "%(null_value)s|%(service_uid)s|%(service_name)s|%(type_id)s|%(data_field_modified)s|%(action)s"
        "|%(data_changes)s|%(null_value)s|message=%(message)s|correlationId=%(correlation_id)s|"
        "elapsedTime=%(null_value)s|execution_time=%(null_value)s"
    )
    assert service_update_logger.service_uid == SERVICE_UID
    assert service_update_logger.service_name == SERVICE_NAME
    assert service_update_logger.type_id == TYPE_ID


def test_service_update_logger_get_action_name_remove(service_update_logger: ServiceUpdateLogger):
    # Act
    action = service_update_logger.get_action_name("remove")
    # Assert
    assert action == "delete"


@mark.parametrize("expected_action", ["update", "add", "delete", "other"])
def test_service_update_logger_get_action_name_other(expected_action: str, service_update_logger: ServiceUpdateLogger):
    # Act
    action = service_update_logger.get_action_name(expected_action)
    # Assert
    assert expected_action == action


def test_service_update_logger_get_opening_times_change_modify(service_update_logger: ServiceUpdateLogger):
    # Arrange
    previous_value = "Test123"
    new_value = "321Test"
    data_field_modified = "test_field"
    # Act
    response = service_update_logger.get_opening_times_change(
        data_field_modified=data_field_modified, previous_value=previous_value, new_value=new_value
    )
    assert (
        f"{data_field_modified}_existing={previous_value}",
        f"{data_field_modified}_update=remove={previous_value}add={new_value}",
    ) == response


def test_service_update_logger_get_opening_times_change_remove(service_update_logger: ServiceUpdateLogger):
    # Arrange
    previous_value = "Test123"
    new_value = ""
    data_field_modified = "test_field"
    # Act
    response = service_update_logger.get_opening_times_change(
        data_field_modified=data_field_modified, previous_value=previous_value, new_value=new_value
    )
    assert (
        f"{data_field_modified}_existing={previous_value}",
        f"{data_field_modified}_update=remove={previous_value}",
    ) == response


def test_service_update_logger_get_opening_times_change_add(service_update_logger: ServiceUpdateLogger):
    # Arrange
    previous_value = ""
    new_value = "321Test"
    data_field_modified = "test_field"
    # Act
    response = service_update_logger.get_opening_times_change(
        data_field_modified=data_field_modified, previous_value=previous_value, new_value=new_value
    )
    assert (
        f"{data_field_modified}_existing={previous_value}",
        f"{data_field_modified}_update=add={new_value}",
    ) == response


def test_service_update_logger_log_service_update(capsys: CaptureFixture):
    # Arrange
    service_update_logger = ServiceUpdateLogger(service_uid=SERVICE_UID, service_name=SERVICE_NAME, type_id=TYPE_ID)
    data_field_modified = "test_field"
    action = "update"
    previous_value = "test_value"
    new_value = "new_test_value"
    environ["ENV"] = environment = "test"
    # Act
    service_update_logger.log_service_update(
        data_field_modified=data_field_modified, action=action, previous_value=previous_value, new_value=new_value
    )
    # Assert
    captured = capsys.readouterr()
    assert (
        f"|INFO|DOS_INTEGRATION_{environment.upper()}|1|DOS_INTEGRATION|NULL|{SERVICE_UID}"
        f'|{SERVICE_NAME}|{TYPE_ID}|{data_field_modified}|{action}|"{previous_value}"|"{new_value}"|NULL|'
        f"message=UpdateService|correlationId=1|elapsedTime=NULL|execution_time=NULL"
    ) in captured.err
    # Cleanup
    del environ["ENV"]
