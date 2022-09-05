from itertools import chain
from logging import Formatter, INFO, Logger, StreamHandler
from os import getenv
from typing import Any, Dict, List, Optional, Union

from aws_lambda_powertools.logging import Logger as PowerToolsLogger

from .changes_to_dos import ChangesToDoS
from .service_histories import ServiceHistories
from common.constants import DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY, DOS_STANDARD_OPENING_TIMES_CHANGE_KEY_LIST
from common.opening_times import opening_period_times_from_list, SpecifiedOpeningTime, StandardOpeningTimes

logger = PowerToolsLogger(child=True)


class ServiceUpdateLogger:
    """A class to handle specfic logs to be sent to DoS Splunk"""

    NULL_VALUE: str = "NULL"
    # Format of the log message, will fail if logged to without the extra fields set
    dos_format = (
        "%(asctime)s|%(levelname)s|DOS_INTEGRATION_%(environment)s|%(correlation_id)s|DOS_INTEGRATION|"
        "%(null_value)s|%(service_uid)s|%(service_name)s|%(type_id)s|%(data_field_modified)s|%(action)s|"
        "%(data_changes)s|%(null_value)s|message=%(message)s|correlationId=%(correlation_id)s|"
        "elapsedTime=%(null_value)s|execution_time=%(null_value)s"
    )
    dos_logger: Logger
    logger: PowerToolsLogger

    def __init__(self, service_uid: str, service_name: str, type_id: str) -> None:
        # Create new logger / get existing logger
        self.dos_logger = Logger("dos_logger")
        self.logger = PowerToolsLogger(child=True)
        # Set to log to stdout
        stream_handler = StreamHandler()
        # Set the format of the log message
        stream_handler.setFormatter(Formatter(self.dos_format))
        # Add the stream handler to the logger
        self.dos_logger.addHandler(stream_handler)
        self.dos_logger.setLevel(INFO)
        # Extra fields to be set in the logger
        self.service_uid = service_uid
        self.service_name = service_name
        self.type_id = type_id
        self.correlation_id = self.logger.get_correlation_id()

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
    ) -> tuple[str, str]:
        """Get the opening times change in the format required for the log message

        Args:
            data_field_modified (str): The dos change name for field that was modified e.g cmsopentimemonday
            previous_value (Optional[str]): The previous value of the field
            new_value (Optional[str]): The new value of the field

        Returns:
            tuple[str, str]: The formatted previous and new values
        """
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
        return existing_value, updated_value

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
                "null_value": self.NULL_VALUE,
                "service_name": self.service_name,
                "service_uid": self.service_uid,
                "type_id": self.type_id,
            },
        )
        self.dos_logger.info(
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
        existing_value, updated_value = self.get_opening_times_change(data_field_modified, previous_value, new_value)

        self.log_service_update(
            data_field_modified=data_field_modified,
            action=action,
            previous_value=existing_value,
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
        existing_value, updated_value = self.get_opening_times_change(
            DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY, previous_value, new_value
        )

        self.log_service_update(
            data_field_modified=DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY,
            action=action,
            previous_value=existing_value,
            new_value=updated_value,
        )


def log_service_updates(changes_to_dos: ChangesToDoS, service_histories: ServiceHistories) -> None:
    """Logs all service updates to DI Splunk and DoS Splunk.

    This is called after the service has been updated to guarantee
    that all updates have been saved to reduce chance of duplicate updates being logged.

    Args:
        changes_to_dos (ChangesToDoS): The changes to dos
        service_histories (ServiceHistories): The service history for service
    """
    service_update_logger = ServiceUpdateLogger(
        service_uid=str(changes_to_dos.dos_service.uid),
        service_name=changes_to_dos.dos_service.name,
        type_id=str(changes_to_dos.dos_service.typeid),
    )
    most_recent_service_history_entry = list(service_histories.service_history.keys())[0]
    service_history_changes: Dict[str, str] = service_histories.service_history[most_recent_service_history_entry][
        "new"
    ]
    for change_key, change_values in service_history_changes.items():
        change_key: str
        change_values: dict[str, Any]
        if change_key == DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY:
            service_update_logger.log_specified_opening_times_service_update(
                action=change_values["changetype"],
                previous_value=changes_to_dos.current_specified_opening_times,
                new_value=changes_to_dos.new_specified_opening_times,
            )
        elif change_key in DOS_STANDARD_OPENING_TIMES_CHANGE_KEY_LIST:
            service_update_logger.log_standard_opening_times_service_update_for_weekday(
                data_field_modified=change_key,
                action=change_values["changetype"],
                previous_value=changes_to_dos.dos_service.standard_opening_times,
                new_value=changes_to_dos.nhs_entity.standard_opening_times,
                weekday=change_key.removeprefix("cmsopentime"),
            )
        else:
            logger.debug(f"Logging service update for change key {change_key}", extra={"change_values": change_values})
            service_update_logger.log_service_update(
                data_field_modified=change_key,
                action=change_values["changetype"],
                previous_value=change_values["previous"],
                new_value=change_values["data"],
            )
