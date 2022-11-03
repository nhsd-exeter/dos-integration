from importlib import import_module
from sys import modules

modules["opening_times"] = import_module("common.opening_times")
modules["nhs"] = import_module("common.nhs")
modules["dos"] = import_module("common.dos")
modules["errors"] = import_module("common.errors")
