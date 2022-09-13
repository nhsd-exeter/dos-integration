from dataclasses import dataclass
from os import environ
from unittest.mock import MagicMock, patch

from aws_lambda_powertools.utilities.typing import LambdaContext
from pytest import fixture

from application.common.types import EmailMessage
from application.send_email.send_email import lambda_handler, send_email

FILE_PATH = "application.send_email.send_email"
BUCKET = "bucket"
KEY = "key"
EVENT = EmailMessage(
    correlation_id="correlation_id",
    recipient_email_address="test@test.com",
    email_body="This is the email body",
    email_subject="Subject of email",
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


@patch(f"{FILE_PATH}.MIMEMultipart")
@patch(f"{FILE_PATH}.SMTP")
@patch(f"{FILE_PATH}.get_secret")
def test_send_email(mock_get_secret: MagicMock, mock_smtp: MagicMock, mock_mime_multipart: MagicMock):
    # Arrange
    environ["AWS_ACCOUNT_NAME"] = "test"
    environ["EMAIL_SECRET_NAME"] = secret_name = "mock_secret_name"
    email_address = "test@test.com"
    html_content = "This is the email body"
    subject = "Subject of email"
    correlation_id = "correlation_id"
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
        email_address=email_address,
        html_content=html_content,
        subject=subject,
        correlation_id=correlation_id,
    )
    # Assert
    assert response is None
    mock_get_secret.assert_called_once_with(secret_name)
    mock_smtp.assert_called_once_with(host="smtp.office365.com", port=587)
    mock_smtp.return_value.ehlo.assert_called_once()
    mock_smtp.return_value.starttls.assert_called_once()
    mock_smtp.return_value.login.assert_called_once_with(di_system_mailbox_address, di_system_mailbox_password)
    mock_smtp.return_value.sendmail.assert_called_once_with(
        from_addr=di_system_mailbox_address,
        to_addrs=[email_address],
        msg=mock_mime_multipart.return_value.as_string.return_value,
    )
    mock_smtp.return_value.quit.assert_called_once()
    # Clean up
    del environ["AWS_ACCOUNT_NAME"]
    del environ["EMAIL_SECRET_NAME"]
