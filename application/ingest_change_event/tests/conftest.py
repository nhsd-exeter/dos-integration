from pytest import fixture
from testfixtures import LogCapture

from common.tests.conftest import PHARMACY_STANDARD_EVENT, PHARMACY_STANDARD_EVENT_STAFF


@fixture()
def log_capture():
    with LogCapture(names="lambda") as capture:
        yield capture


@fixture
def change_event():
    change_event = PHARMACY_STANDARD_EVENT.copy()
    yield change_event


@fixture
def change_event_staff():
    change_event_staff = PHARMACY_STANDARD_EVENT_STAFF.copy()
    yield change_event_staff
