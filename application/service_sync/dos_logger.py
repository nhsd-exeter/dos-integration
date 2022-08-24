from logging import Formatter, INFO, Logger, StreamHandler
from typing import Any


class DoSLogger:
    format = (
        "%(asctime)s|%(levelname)s|DOS_INTEGRATION|%(service_uid)s|%(service_name)s|%(type_id)s|"
        "%(data_field_modified)s|%(action)s|%(data_changes)s|message=%(message)s|%(correlationId)s"
    )
    logger: Logger

    def __init__(self, correlation_id: str, service_uid: str, service_name: str, type_id: str) -> None:
        # Create a logger
        logger = Logger("dos_logger")
        # Set to log to stdout
        stream_handler = StreamHandler()
        # Set the format of the log message
        stream_handler.setFormatter(Formatter(self.format))
        # Add the stream handler to the logger
        logger.addHandler(stream_handler)
        logger.setLevel(INFO)
        # Extra fields to be set in the logger
        self.correlation_id = correlation_id
        self.service_uid = service_uid
        self.service_name = service_name
        self.type_id = type_id
        # Save the logger for use in the class
        self.logger = logger

    def log_demographics_service_update(
        self, data_field_modified: str, action: str, previous_value: Any, new_value: Any
    ) -> None:
        self.logger.info(
            msg="ServiceUpdate",
            extra={
                "correlationId": self.correlation_id,
                "service_uid": self.service_uid,
                "service_name": self.service_name,
                "type_id": self.type_id,
                "data_field_modified": data_field_modified,
                "action": action,
                "data_changes": f"{previous_value}|{new_value}",
            },
        )
