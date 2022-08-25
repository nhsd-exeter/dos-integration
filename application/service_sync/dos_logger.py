from itertools import chain
from logging import Formatter, INFO, Logger, StreamHandler
from os import getenv
from typing import List, Optional, Union

from common.constants import DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY
from common.opening_times import opening_period_times_from_list, SpecifiedOpeningTime, StandardOpeningTimes


class DoSLogger:
    """A class to handle specfic logs to be sent to DoS Splunk"""

    NULL_VALUE: str = "NULL"
    # Format of the log message, will fail if logged to without the extra fields set
    format = (
        "%(asctime)s|%(levelname)s|DOS_INTEGRATION_%(environment)s|%(correlation_id)s|DOS_INTEGRATION|"
        "%(null_value)s|%(service_uid)s|%(service_name)s|%(type_id)s|%(data_field_modified)s|%(action)s|"
        "%(data_changes)s|%(null_value)s|message=%(message)s|correlationId=%(correlation_id)s|"
        "elapsedTime=%(null_value)s|execution_time=%(null_value)s"
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

    def get_action_name(self, action: str) -> str:
        """Get the action name from the service history action name
        Most actions are the same but remove is instead delete for logging purposes

        Args:
            action (str): Change action for the service history

        Returns:
            str: The action name
        """
        return "delete" if action == "remove" else action

    def get_opening_times_change(
        self, data_field_modified: str, previous_value: Optional[str], new_value: Optional[str]
    ) -> str:
        existing_value = f"{data_field_modified}_existing={previous_value}"
        if previous_value != "" and new_value != "":
            # Modify
            updated_value = f"{data_field_modified}_update=remove={previous_value}add={new_value}"
        elif new_value == "":
            # Remove
            updated_value = f"{data_field_modified}_update=remove={previous_value}"
        else:
            # Add
            updated_value = f"{data_field_modified}_update=add={new_value}"
        return f"{existing_value}|{updated_value}"

    def log_service_update(
        self, data_field_modified: str, action: str, previous_value: Optional[str], new_value: Optional[str]
    ) -> None:
        """Logs a service update to DoS Splunk

        Args:
            data_field_modified (str): The dos change name for field that was modified e.g cmsurl
            action (str): The action that was performed e.g add, remove, update
            previous_value (Optional[str]): The previous value of the field
            new_value (Optional[str]): The new value of the field
        """
        environment = getenv("ENV", "UNKNOWN").upper()
        # Handle the case where the values could be None
        previous_value = "" if previous_value in ["None", "", None] else f'"{previous_value}"'
        new_value = "" if new_value in ["None", "", None] else f'"{new_value}"'
        # Log the message with all the extra fields set
        self.logger.info(
            msg="UpdateService",
            extra={
                "action": self.get_action_name(action),
                "correlation_id": self.correlation_id,
                "data_changes": f"{previous_value}|{new_value}",
                "data_field_modified": data_field_modified,
                "environment": environment,
                "null_value": self.NULL_VALUE,
                "service_name": self.service_name,
                "service_uid": self.service_uid,
                "type_id": self.type_id,
            },
        )

    def log_standard_opening_times_service_update_for_weekday(
        self,
        data_field_modified: str,
        action: str,
        previous_value: Union[StandardOpeningTimes, str],
        new_value: Union[StandardOpeningTimes, str],
        weekday: str,
    ) -> None:
        """Logs a service update to DoS Splunk for a standard opening times update

        Args:
            data_field_modified (str): The dos change name for field that was modified e.g cmsopentimemonday
            action (str): The action that was performed e.g add, remove, update
            previous_value (Union[StandardOpeningTimes, str]): The previous value of the field or empty string if none
            new_value (Union[StandardOpeningTimes, str]): The new value of the field or empty string if none
            weekday (str): The weekday to log the update for e.g monday
        """
        previous_value = (
            opening_period_times_from_list(open_periods=previous_value.get_openings(weekday), with_space=False)
            if not isinstance(previous_value, str)
            else previous_value  # type: ignore
        )
        new_value = (
            opening_period_times_from_list(open_periods=new_value.get_openings(weekday), with_space=False)
            if not isinstance(new_value, str)
            else new_value  # type: ignore
        )
        updated_value = self.get_opening_times_change(data_field_modified, previous_value, new_value)

        self.log_service_update(
            data_field_modified=data_field_modified,
            action=action,
            previous_value=previous_value,
            new_value=updated_value,
        )

    def log_specified_opening_times_service_update(
        self,
        action: str,
        previous_value: Union[List[SpecifiedOpeningTime], str],
        new_value: Union[List[SpecifiedOpeningTime], str],
    ) -> None:
        """Logs a service update to DoS Splunk for a specified opening times update

        Args:
            action (str): The action that was performed e.g add, remove, update
            previous_value (Union[List[SpecifiedOpeningTime], str]): The previous value of the field or empty string if none
            new_value (Union[List[SpecifiedOpeningTime], str]): The new value of the field or empty string if none
        """  # noqa: E501

        def get_and_format_specified_opening_times(
            specified_opening_times: Union[List[SpecifiedOpeningTime], str],
        ) -> str:
            specified_opening_times = (
                [specified_opening_time.export_dos_log_format() for specified_opening_time in specified_opening_times]
                if not isinstance(specified_opening_times, str)
                else previous_value  # type: ignore
            )
            return (
                ",".join(list(chain.from_iterable(specified_opening_times)))
                if isinstance(specified_opening_times, list)
                else ""
            )  # type: ignore

        previous_value = get_and_format_specified_opening_times(previous_value)
        new_value = get_and_format_specified_opening_times(new_value)
        updated_value = self.get_opening_times_change(DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY, previous_value, new_value)

        self.log_service_update(
            data_field_modified=DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY,
            action=action,
            previous_value=previous_value,
            new_value=updated_value,
        )
