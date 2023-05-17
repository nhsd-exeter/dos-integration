import pytest
from testfixtures import LogCapture

from common.tests.conftest import PHARMACY_STANDARD_EVENT


@pytest.fixture()
def log_capture() -> LogCapture:
    """Capture logs.

    Yields:
        LogCapture: Log capture
    """
    with LogCapture(names="lambda") as capture:
        yield capture


@pytest.fixture()
def change_event() -> dict:
    """Generate a change event.

    Returns:
        dict: Change event
    """
    return PHARMACY_STANDARD_EVENT.copy()
