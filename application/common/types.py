from typing import Any, Dict, Optional, TypedDict


class HoldingQueueChangeEventItem(TypedDict):
    """Represents a change event sent to the service matcher lambda via the holding queue"""

    change_event: Dict[str, Any]
    dynamo_record_id: str
    correlation_id: str
    sequence_number: int
    message_received: int


class UpdateRequest(TypedDict):
    """Class to represent the update request payload"""

    change_event: Dict[str, Any]
    service_id: str


class UpdateRequestMetadata(TypedDict):
    """Class to represent the update request metadata"""

    dynamo_record_id: str
    correlation_id: str
    message_received: int
    ods_code: str
    message_deduplication_id: str
    message_group_id: str


class UpdateRequestQueueItem(TypedDict):
    """Class to represent the update request queue item containing the payload and metadata
    Optional fields are for the health check as it does not have a payload or metadata"""

    update_request: Optional[UpdateRequest]
    recipient_id: Optional[str]
    metadata: Optional[UpdateRequestMetadata]
    is_health_check: bool


class EmailFile(TypedDict):
    """Class to represent the email file saved to S3"""

    correlation_id: str
    email_body: str
    email_subject: str
    user_id: str


class EmailMessage(TypedDict):
    """Class to represent the email message for the send email lambda"""

    change_id: str
    correlation_id: str
    email_body: str
    email_subject: str
    recipient_email_address: str
    s3_filename: str
    user_id: str
