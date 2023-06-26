from typing import Any, TypedDict


class HoldingQueueChangeEventItem(TypedDict):
    """Represents a change event sent to the service matcher lambda via the holding queue."""

    change_event: dict[str, Any]
    dynamo_record_id: str
    correlation_id: str
    sequence_number: int
    message_received: int


class UpdateRequest(TypedDict):
    """Class to represent the update request payload."""

    change_event: dict[str, Any]
    service_id: str


class EmailFile(TypedDict):
    """Class to represent the email file saved to S3."""

    correlation_id: str
    email_body: str
    email_subject: str
    user_id: str


class EmailMessage(TypedDict):
    """Class to represent the email message for the send email lambda."""

    change_id: str
    correlation_id: str
    email_body: str
    email_subject: str
    recipient_email_address: str
    s3_filename: str
    user_id: str
