from logging import INFO
from os import environ

from pytest import CaptureFixture, fixture, mark

from application.service_sync.dos_logger import DoSLogger

CORRELATION_ID = "12346"
SERVICE_UID = "12345"
SERVICE_NAME = "Test Service"
TYPE_ID = "1"


@fixture
def dos_logger():
    yield DoSLogger(correlation_id=CORRELATION_ID, service_uid=SERVICE_UID, service_name=SERVICE_NAME, type_id=TYPE_ID)


def test_dos_logger(dos_logger: DoSLogger):
    # Assert
    assert dos_logger.logger.name == "dos_logger"
    assert dos_logger.logger.level == INFO
    assert dos_logger.format == (
        "%(asctime)s|%(levelname)s|DOS_INTEGRATION_%(environment)s|%(correlation_id)s|DOS_INTEGRATION|"
        "%(null_value)s|%(service_uid)s|%(service_name)s|%(type_id)s|%(data_field_modified)s|%(action)s"
        "|%(data_changes)s|%(null_value)s|message=%(message)s|correlationId=%(correlation_id)s|"
        "elapsedTime=%(null_value)s|execution_time=%(null_value)s"
    )
    assert dos_logger.correlation_id == CORRELATION_ID
    assert dos_logger.service_uid == SERVICE_UID
    assert dos_logger.service_name == SERVICE_NAME
    assert dos_logger.type_id == TYPE_ID


def test_dos_logger_get_action_name_remove(dos_logger: DoSLogger):
    # Act
    action = dos_logger.get_action_name("remove")
    # Assert
    assert action == "delete"


@mark.parametrize("expected_action", ["update", "add", "delete", "other"])
def test_dos_logger_get_action_name_other(expected_action: str, dos_logger: DoSLogger):
    # Act
    action = dos_logger.get_action_name(expected_action)
    # Assert
    assert expected_action == action


def test_dos_logger_get_opening_times_change_modify(dos_logger: DoSLogger):
    # Arrange
    previous_value = "Test123"
    new_value = "321Test"
    data_field_modified = "test_field"
    # Act
    response = dos_logger.get_opening_times_change(
        data_field_modified=data_field_modified, previous_value=previous_value, new_value=new_value
    )
    assert (
        f"{data_field_modified}_existing={previous_value}",
        f"{data_field_modified}_update=remove={previous_value}add={new_value}",
    ) == response


def test_dos_logger_get_opening_times_change_remove(dos_logger: DoSLogger):
    # Arrange
    previous_value = "Test123"
    new_value = ""
    data_field_modified = "test_field"
    # Act
    response = dos_logger.get_opening_times_change(
        data_field_modified=data_field_modified, previous_value=previous_value, new_value=new_value
    )
    assert (
        f"{data_field_modified}_existing={previous_value}",
        f"{data_field_modified}_update=remove={previous_value}",
    ) == response


def test_dos_logger_get_opening_times_change_add(dos_logger: DoSLogger):
    # Arrange
    previous_value = ""
    new_value = "321Test"
    data_field_modified = "test_field"
    # Act
    response = dos_logger.get_opening_times_change(
        data_field_modified=data_field_modified, previous_value=previous_value, new_value=new_value
    )
    assert (
        f"{data_field_modified}_existing={previous_value}",
        f"{data_field_modified}_update=add={new_value}",
    ) == response


def test_dos_logger_log_service_update(capsys: CaptureFixture):
    # Arrange
    dos_logger = DoSLogger(
        correlation_id=CORRELATION_ID, service_uid=SERVICE_UID, service_name=SERVICE_NAME, type_id=TYPE_ID
    )
    data_field_modified = "test_field"
    action = "update"
    previous_value = "test_value"
    new_value = "new_test_value"
    environ["ENV"] = environment = "test"
    # Act
    dos_logger.log_service_update(
        data_field_modified=data_field_modified, action=action, previous_value=previous_value, new_value=new_value
    )
    # Assert
    captured = capsys.readouterr()
    assert (
        f"|INFO|DOS_INTEGRATION_{environment.upper()}|{CORRELATION_ID}|DOS_INTEGRATION|NULL|{SERVICE_UID}"
        f'|{SERVICE_NAME}|{TYPE_ID}|{data_field_modified}|{action}|"{previous_value}"|"{new_value}"|NULL|'
        f"message=UpdateService|correlationId={CORRELATION_ID}|elapsedTime=NULL|execution_time=NULL"
    ) in captured.err
    # Cleanup
    del environ["ENV"]
