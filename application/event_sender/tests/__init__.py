from sys import modules
from importlib import import_module
from unittest.mock import patch

modules["change_request_logger"] = import_module("event_sender.change_request_logger")
modules["change_request"] = import_module("event_sender.change_request")
patch("common.encryption.validate_event_is_signed", lambda x: x).start()
