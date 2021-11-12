from sys import modules
from importlib import import_module

modules["change_event_exceptions"] = import_module("event_receiver.change_event_exceptions")
modules["change_event_responses"] = import_module("event_receiver.change_event_responses")
modules["change_event_validation"] = import_module("event_receiver.change_event_validation")
