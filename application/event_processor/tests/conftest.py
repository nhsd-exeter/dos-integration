import os
from random import choices, randint, uniform
import json
from pathlib import Path

from pytest import fixture
from testfixtures import LogCapture


std_event_path = os.path.join(Path(__file__).parent.resolve(), "STANDARD_EVENT.json")
with open(std_event_path, "r") as file:
    PHARMACY_STANDARD_EVENT = json.load(file)


@fixture()
def log_capture():
    with LogCapture(names="lambda") as capture:
        yield capture


@fixture
def change_event():
    change_event = PHARMACY_STANDARD_EVENT.copy()
    yield change_event
