from itertools import chain
from logging import INFO, Formatter, Logger, StreamHandler
from os import getenv
from typing import Any, Self

from aws_lambda_powertools.logging import Logger as PowerToolsLogger

from .data_processing.changes_to_dos import ChangesToDoS
from .data_processing.service_histories import ServiceHistories
from .reporting import log_service_updated
from common.constants import (
    DOS_INTEGRATION_USER_NAME,
    DOS_SGSDID_CHANGE_KEY,
    DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_CHANGE_KEY_LIST,
)
from common.dos import DoSService
from common.opening_times import SpecifiedOpeningTime, StandardOpeningTimes, opening_period_times_from_list

logger = PowerToolsLogger(child=True)


class ServiceUpdateLogger:
    """A class to handle specfic logs to be sent to DoS Splunk."""

    NULL_VALUE: str = "NULL"
    dos_basic_format = "%(asctime)s|%(levelname)s|DOS_INTEGRATION_%(environment)s|%(message)s"
    dos_logger: Logger
    logger: PowerToolsLogger
    dos_service: DoSService | None

    def __init__(
        self: Self,
        service_uid: str,
        service_name: str,
        type_id: str,
        odscode: str,
        dos_service: DoSService = None,
    ) -> None:
        """Initialise the ServiceUpdateLogger.

        Args:
            service_uid (str): The service uid
            service_name (str): The service name
            type_id (str): The service type id
            odscode (str): The service odscode
            dos_service (DoSService, optional): The DoSService object. Defaults to None.
        """
        # Create new logger / get existing logger
        self.dos_logger = Logger("dos_logger")
        self.logger = PowerToolsLogger(child=True)
        # Set to log to stdout
        stream_handler = StreamHandler()
        # Set the format of the log message
        stream_handler.setFormatter(Formatter(self.dos_basic_format))
        # Add the stream handler to the logger
        self.dos_logger.addHandler(stream_handler)
        self.dos_logger.setLevel(INFO)
        # Extra fields to be set in the logger
        self.service_uid = service_uid
        self.service_name = service_name
        self.type_id = type_id
        self.odscode = odscode
        self.correlation_id = self.logger.get_correlation_id()
        self.environment = getenv("ENVIRONMENT", "UNKNOWN").upper()
        self.dos_service = dos_service

    def get_opening_times_change(
        self: Self,
        data_field_modified: str,
        previous_value: str | None,
        new_value: str | None,
    ) -> tuple[str, str]:
        """Get the opening times change in the format required for the log message.

        Args:
            data_field_modified (str): The dos change name for field that was modified e.g cmsopentimemonday
            previous_value (Optional[str]): The previous value of the field
            new_value (Optional[str]): The new value of the field

        Returns:
            tuple[str, str]: The formatted previous and new values
        """
        existing_value = f"{data_field_modified}_existing={previous_value}" if previous_value else previous_value
        if previous_value and new_value:
            # Modify
            updated_value = f"{data_field_modified}_update=remove={previous_value}add={new_value}"
        elif not new_value:
            # Remove
            updated_value = f"{data_field_modified}_update=remove={previous_value}"
        else:
            # Add
            updated_value = f"{data_field_modified}_update=add={new_value}"
        return existing_value, updated_value

    def log_service_update(
        self: Self,
        data_field_modified: str,
        action: str,
        previous_value: str | None,
        new_value: str | None,
    ) -> None:
        """Logs a service update to DoS Splunk.

        Args:
            data_field_modified (str): The dos change name for field that was modified e.g cmsurl
            action (str): The action that was performed e.g add, remove, update
            previous_value (Optional[str]): The previous value of the field
            new_value (Optional[str]): The new value of the field
        """
        # Handle the case where the values could be None
        previous_value = "" if previous_value in ["None", "", None] else f'"{previous_value}"'
        new_value = "" if new_value in ["None", "", None] else f'"{new_value}"'
        # Log the message with all the extra fields set
        log_service_updated(
            action=action,
            data_field_modified=data_field_modified,
            new_value=new_value,
            previous_value=previous_value,
            service_name=self.service_name,
            service_uid=self.service_uid,
            type_id=self.type_id,
            dos_service=self.dos_service,
        )

        self.dos_logger.info(
            msg=(
                f"{self.correlation_id}|{DOS_INTEGRATION_USER_NAME}|{self.NULL_VALUE}|{self.service_uid}|"
                f"{self.service_name}|{self.type_id}|{data_field_modified}|{action}|"
                f"{previous_value}|{new_value}|{self.NULL_VALUE}|message=UpdateService|"
                f"correlationId={self.correlation_id}|elapsedTime={self.NULL_VALUE}|execution_time={self.NULL_VALUE}"
            ),
            extra={"environment": self.environment},
        )

    def log_standard_opening_times_service_update_for_weekday(
        self: Self,
        data_field_modified: str,
        action: str,
        previous_value: StandardOpeningTimes | str,
        new_value: StandardOpeningTimes | str,
        weekday: str,
    ) -> None:
        """Logs a service update to DoS Splunk for a standard opening times update.

        Args:
            data_field_modified (str): The dos change name for field that was modified e.g cmsopentimemonday
            action (str): The action that was performed e.g add, remove, update
            previous_value (Union[StandardOpeningTimes, str]): The previous value of the field or empty string if none
            new_value (Union[StandardOpeningTimes, str]): The new value of the field or empty string if none
            weekday (str): The weekday to log the update for e.g monday
        """
        previous_value = (
            previous_value
            if isinstance(previous_value, str)
            else opening_period_times_from_list(open_periods=previous_value.get_openings(weekday), with_space=False)
        )
        new_value = (
            new_value
            if isinstance(new_value, str)
            else opening_period_times_from_list(open_periods=new_value.get_openings(weekday), with_space=False)
        )
        existing_value, updated_value = self.get_opening_times_change(data_field_modified, previous_value, new_value)

        self.log_service_update(
            data_field_modified=data_field_modified,
            action=action,
            previous_value=existing_value,
            new_value=updated_value,
        )

    def log_specified_opening_times_service_update(
        self: Self,
        action: str,
        previous_value: list[SpecifiedOpeningTime] | None,
        new_value: list[SpecifiedOpeningTime] | None,
    ) -> None:
        """Logs a service update to DoS Splunk for a specified opening times update.

        Args:
            action (str): The action that was performed e.g add, remove, update
            previous_value (Optional[List[SpecifiedOpeningTime]]): The previous value of the field or none
            new_value (Optional[List[SpecifiedOpeningTime]]): The new value of the field or none
        """

        def get_and_format_specified_opening_times(
            specified_opening_times: list[SpecifiedOpeningTime] | None,
        ) -> str:
            specified_opening_times = (
                [specified_opening_time.export_dos_log_format() for specified_opening_time in specified_opening_times]
                if specified_opening_times is not None
                else ""
            )
            return (
                ",".join(list(chain.from_iterable(specified_opening_times)))
                if isinstance(specified_opening_times, list)
                else ""
            )

        previous_value = get_and_format_specified_opening_times(previous_value)
        new_value = get_and_format_specified_opening_times(new_value)
        existing_value, updated_value = self.get_opening_times_change(
            DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY,
            previous_value,
            new_value,
        )

        self.log_service_update(
            data_field_modified=DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY,
            action=action,
            previous_value=existing_value,
            new_value=updated_value,
        )

    def log_rejected_change(self: Self, change_id: str) -> None:
        """Logs a rejected change to DoS Splunk.

        Args:
            change_id (str): The change id to log
        """
        self.dos_logger.info(
            msg=(
                f"update|{self.correlation_id}|{self.NULL_VALUE}|{DOS_INTEGRATION_USER_NAME}|RejectDeleteChange|"
                f"request|success|action=reject|changeId={change_id}|org_id={self.service_uid}|"
                f"org_name={self.service_name}|change_status=PENDING|info=change rejected|"
                f"execution_time={self.NULL_VALUE}"
            ),
            extra={"environment": self.environment},
        )

    def log_sgsdid_service_update(self: Self, action: str, new_value: str) -> None:
        """Logs a service update to DoS Splunk for a sgsdid update.

        Args:
            action (str): The action that was performed e.g add, remove, update
            new_value (str): The new value of the field
        """
        add_or_remove = "add" if action == "add" else "remove"
        self.log_service_update(
            data_field_modified=DOS_SGSDID_CHANGE_KEY,
            action=action,
            previous_value="",
            new_value=f"cmssgsdid_update={add_or_remove}={new_value}",
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
        odscode=str(changes_to_dos.nhs_entity.odscode),
        dos_service=changes_to_dos.dos_service,
    )
    most_recent_service_history_entry = next(iter(service_histories.service_history.keys()))
    service_history_changes: dict[str, str] = service_histories.service_history[most_recent_service_history_entry][
        "new"
    ]
    for change_key, change_values in service_history_changes.items():
        change_key: str
        change_values: dict[str, Any]
        if change_key == DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY:
            service_update_logger.log_specified_opening_times_service_update(
                action=change_values.get("changetype", "UNKNOWN"),
                previous_value=changes_to_dos.current_specified_opening_times,
                new_value=changes_to_dos.new_specified_opening_times,
            )
        elif change_key in DOS_STANDARD_OPENING_TIMES_CHANGE_KEY_LIST:
            service_update_logger.log_standard_opening_times_service_update_for_weekday(
                data_field_modified=change_key,
                action=change_values.get("changetype", "UNKNOWN"),
                previous_value=changes_to_dos.dos_service.standard_opening_times,
                new_value=changes_to_dos.nhs_entity.standard_opening_times,
                weekday=change_key.removeprefix("cmsopentime"),
            )
        elif change_key == DOS_SGSDID_CHANGE_KEY:
            service_update_logger.log_sgsdid_service_update(
                action=change_values.get("changetype", "UNKNOWN"),
                new_value=change_values.get("data", {}).get(
                    "add" if change_values.get("changetype") != "delete" else "remove",
                    ["UNKNOWN"],
                )[0],
            )
        else:
            service_update_logger.log_service_update(
                data_field_modified=change_key,
                action=change_values["changetype"],
                previous_value=change_values.get("previous", ""),
                new_value=change_values["data"],
            )
        logger.debug(f"Logging service update for change key {change_key}", change_values=change_values)
