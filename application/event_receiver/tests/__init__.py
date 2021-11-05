from sys import modules
from importlib import import_module

modules["event_validation"] = import_module("event_receiver.event_validation")
