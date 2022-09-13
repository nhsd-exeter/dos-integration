from random import choices
from unittest.mock import MagicMock, patch

from pytest import CaptureFixture
from pytz import timezone

from application.service_sync.pending_changes import (
    build_change_rejection_email_contents,
    check_and_remove_pending_dos_changes,
    get_pending_changes,
    log_rejected_changes,
    PendingChange,
    reject_pending_changes,
    send_rejection_emails,
)

FILE_PATH = "application.service_sync.pending_changes"
ROW = {
    "id": "".join(choices("ABCDEFGHIJKLM", k=8)),
    "type": "".join(choices("ABCDEFGHIJKLM", k=8)),
    "value": "".join(choices("ABCDEFGHIJKLM", k=8)),
    "creatorsname": "".join(choices("ABCDEFGHIJKLM", k=8)),
    "email": "".join(choices("ABCDEFGHIJKLM", k=8)),
    "typeid": "".join(choices("ABCDEFGHIJKLM", k=8)),
    "name": "".join(choices("ABCDEFGHIJKLM", k=8)),
    "uid": "".join(choices("ABCDEFGHIJKLM", k=8)),
}
EXPECTED_QUERY = (
    "SELECT c.id, c.value, c.creatorsname, u.email, s.typeid, s.name, s.uid "
    "FROM changes c LEFT JOIN users u ON u.username = c.creatorsname "
    "LEFT JOIN services s ON s.id = c.serviceid "
    "WHERE serviceid=%(SERVICE_ID)s AND approvestatus='PENDING'"
)


def test_pending_change():
    # Act
    pending_change = PendingChange(ROW)
    # Assert
    assert pending_change.id == ROW["id"]
    assert pending_change.value == ROW["value"]
    assert pending_change.creatorsname == ROW["creatorsname"]
    assert pending_change.email == ROW["email"]
    assert pending_change.typeid == ROW["typeid"]
    assert pending_change.name == ROW["name"]
    assert pending_change.uid == ROW["uid"]


def test_pending_change_is_valid_true():
    # Arrange
    pending_change = PendingChange(ROW)
    pending_change.value = '{"new": {"cmsurl": "test"}}'
    # Act
    is_valid = pending_change.is_valid()
    # Assert
    assert True is is_valid


def test_pending_change_is_valid_false():
    # Arrange
    pending_change = PendingChange(ROW)
    pending_change.value = '{"new": {"name": "test"}}'
    # Act
    is_valid = pending_change.is_valid()
    # Assert
    assert False is is_valid


def test_pending_change_is_valid_exception():
    # Arrange
    pending_change = PendingChange(ROW)
    pending_change.value = '{"new": {"name": "test"}'
    # Act
    is_valid = pending_change.is_valid()
    # Assert
    assert False is is_valid


@patch(f"{FILE_PATH}.send_rejection_emails")
@patch(f"{FILE_PATH}.log_rejected_changes")
@patch(f"{FILE_PATH}.reject_pending_changes")
@patch(f"{FILE_PATH}.get_pending_changes")
@patch(f"{FILE_PATH}.connect_to_dos_db")
def test_check_and_remove_pending_dos_changes(
    mock_connect_to_dos_db: MagicMock,
    mock_get_pending_changes: MagicMock,
    mock_reject_pending_changes: MagicMock,
    mock_log_rejected_changes: MagicMock,
    mock_send_rejection_emails: MagicMock,
):
    # Arrange
    service_id = "test"
    mock_get_pending_changes.return_value = get_pending_changes_response = [PendingChange(ROW)]
    # Act
    response = check_and_remove_pending_dos_changes(service_id)
    # Assert
    assert None is response
    mock_connect_to_dos_db.assert_called_once()
    mock_get_pending_changes.assert_called_once_with(
        connection=mock_connect_to_dos_db.return_value.__enter__.return_value, service_id=service_id
    )
    mock_reject_pending_changes.assert_called_once_with(
        connection=mock_connect_to_dos_db.return_value.__enter__.return_value,
        pending_changes=get_pending_changes_response,
    )
    mock_log_rejected_changes.assert_called_once_with(get_pending_changes_response)
    mock_send_rejection_emails.assert_called_once_with(get_pending_changes_response)


@patch(f"{FILE_PATH}.send_rejection_emails")
@patch(f"{FILE_PATH}.log_rejected_changes")
@patch(f"{FILE_PATH}.reject_pending_changes")
@patch(f"{FILE_PATH}.get_pending_changes")
@patch(f"{FILE_PATH}.connect_to_dos_db")
def test_check_and_remove_pending_dos_changes_no_pending_changes(
    mock_connect_to_dos_db: MagicMock,
    mock_get_pending_changes: MagicMock,
    mock_reject_pending_changes: MagicMock,
    mock_log_rejected_changes: MagicMock,
    mock_send_rejection_emails: MagicMock,
):
    # Arrange
    service_id = "test"
    mock_get_pending_changes.return_value = None
    # Act
    response = check_and_remove_pending_dos_changes(service_id)
    # Assert
    assert None is response
    mock_connect_to_dos_db.assert_called_once()
    mock_get_pending_changes.assert_called_once_with(
        connection=mock_connect_to_dos_db.return_value.__enter__.return_value, service_id=service_id
    )
    mock_reject_pending_changes.assert_not_called()
    mock_log_rejected_changes.assert_not_called()
    mock_send_rejection_emails.assert_not_called()


@patch(f"{FILE_PATH}.send_rejection_emails")
@patch(f"{FILE_PATH}.log_rejected_changes")
@patch(f"{FILE_PATH}.reject_pending_changes")
@patch(f"{FILE_PATH}.get_pending_changes")
@patch(f"{FILE_PATH}.connect_to_dos_db")
def test_check_and_remove_pending_dos_changes_invalid_changes(
    mock_connect_to_dos_db: MagicMock,
    mock_get_pending_changes: MagicMock,
    mock_reject_pending_changes: MagicMock,
    mock_log_rejected_changes: MagicMock,
    mock_send_rejection_emails: MagicMock,
):
    # Arrange
    service_id = "test"
    mock_get_pending_changes.return_value = []
    # Act
    response = check_and_remove_pending_dos_changes(service_id)
    # Assert
    assert None is response
    mock_connect_to_dos_db.assert_called_once()
    mock_get_pending_changes.assert_called_once_with(
        connection=mock_connect_to_dos_db.return_value.__enter__.return_value, service_id=service_id
    )
    mock_reject_pending_changes.assert_not_called()
    mock_log_rejected_changes.assert_not_called()
    mock_send_rejection_emails.assert_not_called()


@patch(f"{FILE_PATH}.PendingChange.is_valid")
@patch(f"{FILE_PATH}.query_dos_db")
def test_get_pending_changes_is_pending_changes_valid_changes(mock_query_dos_db: MagicMock, mock_is_valid: MagicMock):
    # Arrange
    connection = MagicMock()
    service_id = "test"
    mock_query_dos_db.return_value.fetchall.return_value = [ROW]
    mock_is_valid.return_value = True
    # Act
    response = get_pending_changes(connection, service_id)
    # Assert
    mock_query_dos_db.assert_called_once_with(
        connection=connection,
        query=EXPECTED_QUERY,
        vars={"SERVICE_ID": service_id},
    )
    mock_is_valid.assert_called_once()
    assert PendingChange(ROW) == response[0]


@patch(f"{FILE_PATH}.PendingChange.is_valid")
@patch(f"{FILE_PATH}.query_dos_db")
def test_get_pending_changes_is_pending_changes_invalid_changes(mock_query_dos_db: MagicMock, mock_is_valid: MagicMock):
    # Arrange
    connection = MagicMock()
    service_id = "test"
    mock_query_dos_db.return_value.fetchall.return_value = [ROW]
    mock_is_valid.return_value = False
    # Act
    response = get_pending_changes(connection, service_id)
    # Assert
    mock_query_dos_db.assert_called_once_with(
        connection=connection,
        query=EXPECTED_QUERY,
        vars={"SERVICE_ID": service_id},
    )
    mock_is_valid.assert_called_once()
    assert response == []


@patch(f"{FILE_PATH}.PendingChange.is_valid")
@patch(f"{FILE_PATH}.query_dos_db")
def test_get_pending_changes_no_changes(mock_query_dos_db: MagicMock, mock_is_valid: MagicMock):
    # Arrange
    connection = MagicMock()
    service_id = "test"
    mock_query_dos_db.return_value.fetchall.return_value = []
    mock_is_valid.return_value = False
    # Act
    response = get_pending_changes(connection, service_id)
    # Assert
    mock_query_dos_db.assert_called_once_with(
        connection=connection,
        query=EXPECTED_QUERY,
        vars={"SERVICE_ID": service_id},
    )
    mock_is_valid.assert_not_called()
    assert None is response


@patch(f"{FILE_PATH}.datetime")
@patch(f"{FILE_PATH}.query_dos_db")
def test_reject_pending_changes_single_rejection(mock_query_dos_db: MagicMock, mock_datetime: MagicMock):
    # Arrange
    pending_change = PendingChange(ROW)
    pending_changes = [pending_change]
    connection = MagicMock()
    # Act
    response = reject_pending_changes(connection, pending_changes)
    # Assert
    assert None is response
    mock_datetime.now.assert_called_once_with(timezone("Europe/London"))
    mock_query_dos_db.assert_called_once_with(
        connection=connection,
        query=(
            "UPDATE changes SET approvestatus='REJECTED',"
            f"modifiedtimestamp=%(TIMESTAMP)s, modifiersname=%(USER_NAME)s WHERE id='{pending_change.id}'"
        ),
        vars={"USER_NAME": "DOS_INTEGRATION", "TIMESTAMP": mock_datetime.now.return_value},
    )


@patch(f"{FILE_PATH}.datetime")
@patch(f"{FILE_PATH}.query_dos_db")
def test_reject_pending_changes_multiple_rejections(mock_query_dos_db: MagicMock, mock_datetime: MagicMock):
    # Arrange
    pending_change1 = PendingChange(ROW)
    pending_change1.id = "Change1"
    pending_change2 = PendingChange(ROW)
    pending_change2.id = "Change2"
    pending_change3 = PendingChange(ROW)
    pending_change3.id = "Change3"
    pending_changes = [pending_change1, pending_change2, pending_change3]
    connection = MagicMock()
    # Act
    response = reject_pending_changes(connection, pending_changes)
    # Assert
    assert None is response
    mock_datetime.now.assert_called_once_with(timezone("Europe/London"))
    mock_query_dos_db.assert_called_once_with(
        connection=connection,
        query=(
            "UPDATE changes SET approvestatus='REJECTED',"
            f"modifiedtimestamp=%(TIMESTAMP)s, modifiersname=%(USER_NAME)s "
            f"WHERE id in ('{pending_change1.id}','{pending_change2.id}','{pending_change3.id}')"
        ),
        vars={"USER_NAME": "DOS_INTEGRATION", "TIMESTAMP": mock_datetime.now.return_value},
    )


def test_log_rejected_changes(capsys: CaptureFixture):
    # Arrange
    pending_change = PendingChange(ROW)
    pending_changes = [pending_change]
    # Act
    response = log_rejected_changes(pending_changes)
    # Assert
    assert None is response
    captured = capsys.readouterr()
    assert (
        f"update|1|NULL|DOS_INTEGRATION|RejectDeleteChange|"
        f"request|success|action=reject|changeId={pending_change.id}|org_id={pending_change.uid}|"
        f"org_name={pending_change.name}|change_status=PENDING|info=change rejected|"
        "execution_time=NULL"
    ) in captured.err


@patch(f"{FILE_PATH}.remove")
@patch(f"{FILE_PATH}.build_change_rejection_email_contents")
@patch(f"{FILE_PATH}.time_ns")
@patch(f"{FILE_PATH}.dump")
@patch("builtins.open")
@patch(f"{FILE_PATH}.put_email_to_s3")
def test_send_rejection_emails(
    mock_put_email_to_s3: MagicMock,
    mock_open: MagicMock,
    mock_dump: MagicMock,
    mock_time_ns: MagicMock,
    mock_build_change_rejection_email_contents: MagicMock,
    mock_remove: MagicMock,
):
    # Arrange
    pending_change = PendingChange(ROW)
    pending_changes = [pending_change]
    mock_build_change_rejection_email_contents.return_value = email_contents = "test"
    expected_file_path = "/tmp/rejection-email.json"
    # Act
    response = send_rejection_emails(pending_changes)
    # Assert
    assert None is response
    mock_dump.assert_called_once_with(
        {
            "correlation_id": "1",
            "recipient_email_address": pending_change.email,
            "email_body": email_contents,
            "email_subject": "Your DoS Change has been rejected",
        },
        mock_open.return_value.__enter__.return_value,
    )
    mock_put_email_to_s3.assert_called_once_with(
        expected_file_path, f"rejection-emails/rejection-email-{mock_time_ns.return_value}.json"
    )
    mock_remove.assert_called_once_with(expected_file_path)


@patch("builtins.open")
def test_build_change_rejection_email_contents(mock_open: MagicMock):
    # Arrange
    pending_change = PendingChange(ROW)
    pending_change.value = '{"new":{"cmsurl":{"previous":"test.com","data":"https://www.test.com"}}}'
    # Act
    response = build_change_rejection_email_contents(pending_change)
    # Assert
    assert (
        response
        == mock_open.return_value.__enter__.return_value.read.return_value.replace.return_value.replace.return_value.replace.return_value.replace.return_value.replace.return_value.replace.return_value.replace.return_value  # noqa: E501
    )
