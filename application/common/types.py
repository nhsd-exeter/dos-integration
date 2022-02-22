from typing import TypedDict, Dict


class ChangeMetadata(TypedDict):
    dynamo_record_id: str
    correlation_id: str
    message_received: int
    ods_code: str
    message_deduplication_id: str
    message_group_id: str


class ChangeRequestQueueItem(TypedDict):
    is_health_check: bool
    change_request: Dict  # could change this to Change Request potentially
    recipient_id: str
    metadata: ChangeMetadata
