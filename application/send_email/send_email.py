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

tracer = Tracer()
logger = Logger()


@tracer.capture_lambda_handler()
@unhandled_exception_logging_hidden_event
@logger.inject_lambda_context(clear_state=True, correlation_id_path="correlation_id")
def lambda_handler(event: EmailMessage, context: LambdaContext) -> None:  # noqa: ARG001
    """Entrypoint handler for the service_sync lambda.

    Args:
        event (EmailMessage): Lambda function invocation event
        context (LambdaContext): Lambda function context object
    """
    logger.append_keys(user_id=event["user_id"], change_id=event["change_id"], s3_filename=event["s3_filename"])
    logger.info("Starting send_email lambda")
    send_email(
        email_address=event["recipient_email_address"],
        html_content=event["email_body"],
        subject=event["email_subject"],
        correlation_id=event["correlation_id"],
    )


def send_email(email_address: str, html_content: str, subject: str, correlation_id: str) -> None:
    """Send an email to the specified email address.

    Args:
        email_address (str): Email address to send the email to
        html_content (str): HTML content of the email
        subject (str): Subject of the email
        correlation_id (str): Correlation ID of the email
    """
    aws_account_name = environ["AWS_ACCOUNT_NAME"]
    if aws_account_name != "nonprod" or "email" in correlation_id:
        logger.info("Preparing to send email")
        email_secrets = get_secret(environ["EMAIL_SECRET_NAME"])
        to_email_address = email_address
        di_system_email_address = email_secrets["DI_SYSTEM_MAILBOX_ADDRESS"]
        di_system_email_password = email_secrets["DI_SYSTEM_MAILBOX_PASSWORD"]
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg.attach(MIMEText(html_content, "html"))
        logger.info("Email content prepared")
        try:
            # Don't log any variables that contain PID or password
            smtp = SMTP(host="smtp.office365.com", port=587, timeout=15)
            logger.info("Connected to SMTP server")
            smtp.ehlo()
            logger.info("Sent EHLO")
            smtp.starttls()
            logger.info("Started TLS")
            smtp.login(di_system_email_address, di_system_email_password)
            logger.info("Logged in to SMTP server")
            smtp.sendmail(from_addr=di_system_email_address, to_addrs=[to_email_address], msg=msg.as_string())
            logger.warning("Sent email", cloudwatch_metric_filter_matching_attribute="EmailSent")
            smtp.quit()
            logger.info("Disconnected from SMTP server")
        except BaseException:
            logger.exception("Email failed", cloudwatch_metric_filter_matching_attribute="EmailFailed")
            msg = "An error occurred while sending the email"
            raise SMTPException(msg) from None
