from dataclasses import dataclass
from datetime import datetime

from .change_event import ChangeEvent


@dataclass(repr=True)
class SmokeTestContext:
    """Context for smoke tests."""

    original_service: ChangeEvent | None = None
    updated_service: ChangeEvent | None = None
    request_start_time: datetime | None = None
