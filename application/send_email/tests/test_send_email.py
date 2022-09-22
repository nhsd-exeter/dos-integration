from dataclasses import dataclass
from os import environ
from smtplib import SMTPException
from unittest.mock import MagicMock, patch

from aws_lambda_powertools.utilities.typing import LambdaContext
from pytest import fixture, raises

from application.common.types import EmailMessage
from application.send_email.send_email import lambda_handler, send_email

FILE_PATH = "application.send_email.send_email"
BUCKET = "bucket"
KEY = "key"
CORRELATION_ID = "correlation_id"
RECIPIENT_EMAIL_ADDRESS = "recipient_email_address"
EMAIL_BODY = "This is the email body"
EMAIL_SUBJECT = "Subject of email"
EVENT = EmailMessage(
    correlation_id=CORRELATION_ID,
    recipient_email_address=RECIPIENT_EMAIL_ADDRESS,
    email_body=EMAIL_BODY,
    email_subject=EMAIL_SUBJECT,
)


@fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        """Mock LambdaContext - All dummy values"""

        function_name: str = "send-email"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:000000000:function:send-email"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()


@patch(f"{FILE_PATH}.send_email")
def test_lambda_handler(mock_send_email: MagicMock, lambda_context: LambdaContext):
    # Arrange
    event = EVENT.copy()
    # Act
    response = lambda_handler(event, lambda_context)
    # Assert
    assert response is None
    mock_send_email.assert_called_once_with(
        email_address=event["recipient_email_address"],
        html_content=event["email_body"],
        subject=event["email_subject"],
        correlation_id=event["correlation_id"],
    )


@patch(f"{FILE_PATH}.add_metric")
@patch(f"{FILE_PATH}.MIMEMultipart")
@patch(f"{FILE_PATH}.SMTP")
@patch(f"{FILE_PATH}.get_secret")
def test_send_email(
    mock_get_secret: MagicMock, mock_smtp: MagicMock, mock_mime_multipart: MagicMock, add_metric: MagicMock
):
    # Arrange
    environ["AWS_ACCOUNT_NAME"] = "test"
    environ["EMAIL_SECRET_NAME"] = secret_name = "mock_secret_name"
    di_team_mailbox_address = "di_team_mailbox_address"
    di_system_mailbox_address = "di_system_mailbox_address"
    di_system_mailbox_password = "di_system_mailbox_password"
    mock_get_secret.return_value = {
        "DI_TEAM_MAILBOX_ADDRESS": di_team_mailbox_address,
        "DI_SYSTEM_MAILBOX_ADDRESS": di_system_mailbox_address,
        "DI_SYSTEM_MAILBOX_PASSWORD": di_system_mailbox_password,
    }
    # Act
    response = send_email(
        email_address=RECIPIENT_EMAIL_ADDRESS,
        html_content=EMAIL_BODY,
        subject=EMAIL_SUBJECT,
        correlation_id=CORRELATION_ID,
    )
    # Assert
    assert response is None
    mock_get_secret.assert_called_once_with(secret_name)
    mock_smtp.assert_called_once_with(host="smtp.office365.com", port=587, timeout=15)
    mock_smtp.return_value.ehlo.assert_called_once()
    mock_smtp.return_value.starttls.assert_called_once()
    mock_smtp.return_value.login.assert_called_once_with(di_system_mailbox_address, di_system_mailbox_password)
    mock_smtp.return_value.sendmail.assert_called_once_with(
        from_addr=di_system_mailbox_address,
        to_addrs=[RECIPIENT_EMAIL_ADDRESS],
        msg=mock_mime_multipart.return_value.as_string.return_value,
    )
    mock_smtp.return_value.quit.assert_called_once()
    add_metric.assert_called_once_with("EmailSent")
    # Clean up
    del environ["AWS_ACCOUNT_NAME"]
    del environ["EMAIL_SECRET_NAME"]


@patch(f"{FILE_PATH}.MIMEMultipart")
@patch(f"{FILE_PATH}.SMTP")
@patch(f"{FILE_PATH}.get_secret")
def test_send_email_nonprod(mock_get_secret: MagicMock, mock_smtp: MagicMock, mock_mime_multipart: MagicMock):
    # Arrange
    environ["AWS_ACCOUNT_NAME"] = "nonprod"
    # Act
    response = send_email(
        email_address=RECIPIENT_EMAIL_ADDRESS,
        html_content=EMAIL_BODY,
        subject=EMAIL_SUBJECT,
        correlation_id=CORRELATION_ID,
    )
    # Assert
    assert response is None
    mock_get_secret.assert_not_called()
    mock_smtp.assert_not_called()
    mock_mime_multipart.assert_not_called()
    # Clean up
    del environ["AWS_ACCOUNT_NAME"]


@patch(f"{FILE_PATH}.add_metric")
@patch(f"{FILE_PATH}.MIMEMultipart")
@patch(f"{FILE_PATH}.SMTP")
@patch(f"{FILE_PATH}.get_secret")
def test_send_email_exception(
    mock_get_secret: MagicMock, mock_smtp: MagicMock, mock_mime_multipart: MagicMock, add_metric: MagicMock
):
    # Arrange
    environ["AWS_ACCOUNT_NAME"] = "test"
    environ["EMAIL_SECRET_NAME"] = secret_name = "mock_secret_name"
    di_team_mailbox_address = "di_team_mailbox_address"
    di_system_mailbox_address = "di_system_mailbox_address"
    di_system_mailbox_password = "di_system_mailbox_password"
    mock_get_secret.return_value = {
        "DI_TEAM_MAILBOX_ADDRESS": di_team_mailbox_address,
        "DI_SYSTEM_MAILBOX_ADDRESS": di_system_mailbox_address,
        "DI_SYSTEM_MAILBOX_PASSWORD": di_system_mailbox_password,
    }
    mock_smtp.return_value.ehlo.side_effect = SMTPException()
    # Act
    with raises(SMTPException, match="An error occurred while sending the email"):
        send_email(
            email_address=RECIPIENT_EMAIL_ADDRESS,
            html_content=EMAIL_BODY,
            subject=EMAIL_SUBJECT,
            correlation_id=CORRELATION_ID,
        )
    # Assert
    mock_get_secret.assert_called_once_with(secret_name)
    mock_smtp.assert_called_once_with(host="smtp.office365.com", port=587, timeout=15)
    mock_smtp.return_value.ehlo.assert_called_once()
    mock_smtp.return_value.starttls.assert_not_called()
    mock_smtp.return_value.login.assert_not_called()
    mock_smtp.return_value.sendmail.assert_not_called()
    mock_smtp.return_value.quit.assert_not_called()
    add_metric.assert_called_once_with("EmailFailed")
    # Clean up
    del environ["AWS_ACCOUNT_NAME"]
    del environ["EMAIL_SECRET_NAME"]
