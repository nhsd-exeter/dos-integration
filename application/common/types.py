from typing import TypedDict, Dict


class ChangeMetadata(TypedDict):
    dynamo_record_id: str
    correlation_id: str
    message_received: int
    ods_code: str


class ChangeRequestQueueItem(TypedDict):
    is_health_check: bool
    change_request: Dict  # could change this to Change Request potentially
    recipient_id: str
    metadata: ChangeMetadata
