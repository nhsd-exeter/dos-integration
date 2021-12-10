from sys import modules
from importlib import import_module

modules["change_request"] = import_module("event_processor.change_request")
modules["opening_times"] = import_module("event_processor.opening_times")
modules["nhs"] = import_module("event_processor.nhs")
modules["dos"] = import_module("event_processor.dos")
modules["changes"] = import_module("event_processor.changes")
