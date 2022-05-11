from sys import modules
from importlib import import_module

modules["change_request"] = import_module("event_processor.change_request")
modules["opening_times"] = import_module("common.opening_times")
modules["nhs"] = import_module("common.nhs")
modules["dos"] = import_module("common.dos")
modules["reporting"] = import_module("event_processor.reporting")
modules["change_event_exceptions"] = import_module("common.change_event_exceptions")
modules["change_event_validation"] = import_module("event_processor.change_event_validation")
modules["changes"] = import_module("event_processor.changes")
