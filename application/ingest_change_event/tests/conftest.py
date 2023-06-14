import pytest
from testfixtures import LogCapture

from application.conftest import PHARMACY_STANDARD_EVENT, PHARMACY_STANDARD_EVENT_STAFF


@pytest.fixture()
def log_capture() -> LogCapture:
    """LogCapture fixture for lambda functions."""
    with LogCapture(names="lambda") as capture:
        yield capture


@pytest.fixture()
def change_event() -> dict:
    """Get a standard change event."""
    return PHARMACY_STANDARD_EVENT.copy()


@pytest.fixture()
def change_event_staff() -> dict:
    """Get a standard change event with staff."""
    return PHARMACY_STANDARD_EVENT_STAFF.copy()
