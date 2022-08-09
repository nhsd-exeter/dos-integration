from typing import Any, Dict, Optional, TypedDict


class UpdateRequest(TypedDict):
    change_event: Dict[str, Any]
    service_id: str


class UpdateRequestMetadata(TypedDict):
    dynamo_record_id: str
    correlation_id: str
    message_received: int
    ods_code: str
    message_deduplication_id: str
    message_group_id: str


class UpdateRequestQueueItem(TypedDict):
    update_request: Optional[UpdateRequest]
    recipient_id: Optional[str]
    metadata: Optional[UpdateRequestMetadata]
    is_health_check: bool
