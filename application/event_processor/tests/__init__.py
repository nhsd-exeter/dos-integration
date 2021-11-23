from sys import modules
from importlib import import_module

modules["nhs"] = import_module("event_processor.nhs")
modules["change_request"] = import_module("event_processor.change_request")
modules["dos"] = import_module("event_processor.dos")
