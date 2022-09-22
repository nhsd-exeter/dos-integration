from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import environ
from smtplib import SMTP, SMTPException

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.tracing import Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

from common.middlewares import unhandled_exception_logging_hidden_event
from common.secretsmanager import get_secret
from common.types import EmailMessage
from common.utilities import add_metric

tracer = Tracer()
logger = Logger()


@tracer.capture_lambda_handler()
@unhandled_exception_logging_hidden_event
@logger.inject_lambda_context
def lambda_handler(event: EmailMessage, context: LambdaContext) -> None:
    """Entrypoint handler for the service_sync lambda

    Args:
        event (EmailMessage): Lambda function invocation event
        context (LambdaContext): Lambda function context object
    """
    logger.set_correlation_id(event["correlation_id"])
    logger.info("Starting send_email lambda")
    send_email(
        email_address=event["recipient_email_address"],
        html_content=event["email_body"],
        subject=event["email_subject"],
        correlation_id=event["correlation_id"],
    )


def send_email(email_address: str, html_content: str, subject: str, correlation_id: str) -> None:
    """Send an email to the specified email address

    Args:
        email_address (str): Email address to send the email to
        html_content (str): HTML content of the email
        subject (str): Subject of the email
        correlation_id (str): Correlation ID of the email
    """
    aws_account_name = environ["AWS_ACCOUNT_NAME"]
    if aws_account_name != "nonprod" or "email" in correlation_id:
        email_secrets = get_secret(environ["EMAIL_SECRET_NAME"])
        to_email_address = email_address
        di_system_email_address = email_secrets["DI_SYSTEM_MAILBOX_ADDRESS"]
        di_system_email_password = email_secrets["DI_SYSTEM_MAILBOX_PASSWORD"]
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg.attach(MIMEText(html_content, "html"))
        logger.info("Sending email")
        try:
            # Don't log any variables that contain PID or password
            smtp = SMTP(host="smtp.office365.com", port=587, timeout=15)
            smtp.ehlo()
            smtp.starttls()
            smtp.login(di_system_email_address, di_system_email_password)
            smtp.sendmail(from_addr=di_system_email_address, to_addrs=[to_email_address], msg=msg.as_string())
            smtp.quit()
            logger.info("Email sent")
            add_metric("EmailSent")  # type: ignore
        except SMTPException:
            add_metric("EmailFailed")  # type: ignore
            logger.error("Email failed")
            raise SMTPException("An error occurred while sending the email")
