from datetime import datetime
from itertools import chain
from json import loads
from time import time
from typing import Any, List

from aws_lambda_powertools.logging import Logger
from psycopg2.extensions import connection
from psycopg2.extras import DictCursor, Json
from pytz import timezone

from .service_histories_change import ServiceHistoriesChange
from common.constants import DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY
from common.dos_db_connection import query_dos_db
from common.opening_times import SpecifiedOpeningTime, StandardOpeningTimes

logger = Logger(child=True)


class ServiceHistories:
    NEW_CHANGE_KEY: str
    service_history: dict[str, Any]
    existing_service_history: dict[str, Any]
    service_id: int
    history_already_exists: bool

    def __init__(self, service_id: int) -> None:
        # Epoch time in seconds rounded down to the nearest second
        self.current_epoch_time = int(time())
        # Use same date/time from epoch time and format it to DoS date/time format
        self.service_id = service_id
        self.history_already_exists = False
        self.existing_service_history = {}
        self.service_history = {}
        self.NEW_CHANGE_KEY = "new_change"

    def get_service_history_from_db(self, connection: connection) -> None:
        """Gets the service_histories json from the database

        Args:
            connection (connection): The connection to the database
        """
        cursor = connection.cursor(cursor_factory=DictCursor)
        # Get the history json from the database for the service
        cursor.execute(f"Select history from servicehistories where serviceid = '{self.service_id}'")
        results: List[Any] = cursor.fetchall()
        if results != []:
            # Change History exists in the database
            logger.debug(f"Service history exists in the database for serviceid {self.service_id}")
            service_history = results[0][0]
            self.existing_service_history = loads(service_history)
            self.history_already_exists = True
        else:
            # Change History does not exist in the database
            logger.warning(f"Service history does not exist in the database for serviceid {self.service_id}")
            self.existing_service_history = {}
            self.history_already_exists = False

    def create_service_histories_entry(self) -> None:
        """Creates a new entry in the service_histories json for any changes that will be made to the service"""
        self.service_history[self.NEW_CHANGE_KEY] = {
            "new": {},
            "initiator": {"userid": "DOS_INTEGRATION", "timestamp": "TBD"},
            "approver": {"userid": "DOS_INTEGRATION", "timestamp": "TBD"},
        }  # Timestamp will be created when the change is sent to db for it to be realtime

    def add_change(self, dos_change_key: str, change: ServiceHistoriesChange) -> None:
        """Adds a change to the updated service_histories json"""
        self.service_history[self.NEW_CHANGE_KEY]["new"][dos_change_key] = change.get_change()

    def add_standard_opening_times_change(
        self,
        current_opening_times: StandardOpeningTimes,
        new_opening_times: StandardOpeningTimes,
        weekday: str,
        dos_weekday_change_key: str,
    ) -> None:
        """Adds a standard opening times change to the updated service_histories json

        Args:
            current_opening_times (StandardOpeningTimes): The current standard opening times
            new_opening_times (StandardOpeningTimes): The new standard opening times
            weekday (str): The weekday for the change
            dos_weekday_change_key (str): The dos_weekday_change_key for the change
        """
        data = {}
        # Get the opening times in the format that is expected by the DoS Service History API
        # Format is time in seconds  e.g. "1000-2000"
        current_opening_times_in_seconds = current_opening_times.export_opening_times_in_seconds_for_day(weekday)
        new_opening_times_in_seconds = new_opening_times.export_opening_times_in_seconds_for_day(weekday)
        # If either list is empty then it doesn't have any open periods, Therefore it's closed
        if current_opening_times_in_seconds != []:
            data["remove"] = current_opening_times_in_seconds
        if new_opening_times_in_seconds != []:
            data["add"] = new_opening_times_in_seconds
        # Add the change to the service history
        self.add_change(
            dos_change_key=dos_weekday_change_key,
            change=ServiceHistoriesChange(
                change_key=dos_weekday_change_key,
                previous_value=current_opening_times.export_opening_times_for_day(weekday),
                data=data,
            ),
        )

    def add_specified_opening_times_change(
        self,
        current_opening_times: List[SpecifiedOpeningTime],
        new_opening_times: List[SpecifiedOpeningTime],
    ) -> None:
        """Adds a change to the updated service_histories json

        Args:
            current_opening_times (List[SpecifiedOpeningTime]): The current specified opening times
            new_opening_times (List[SpecifiedOpeningTime]): The new specified opening times
        """
        # Get the opening times in the format that is expected by the DoS Service History Table
        current_specified_opening_times = self.get_formatted_specified_opening_times(current_opening_times)
        new_specified_opening_times = self.get_formatted_specified_opening_times(new_opening_times)
        data = {}
        if current_specified_opening_times != []:
            data["remove"] = current_specified_opening_times
        if new_specified_opening_times != []:
            data["add"] = new_specified_opening_times
        # Add the change to the service history
        self.add_change(
            dos_change_key=DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY,
            change=ServiceHistoriesChange(
                change_key=DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY,
                previous_value=current_specified_opening_times,
                data=data,
            ),
        )

    def get_formatted_specified_opening_times(self, opening_times: List[SpecifiedOpeningTime]) -> list[str]:
        """Returns the specified opening times in the format that is expected by the DoS Service History

        Args:
            opening_times (List[SpecifiedOpeningTime]): The specified opening times to be formatted

        Returns:
            list: The formatted specified opening times
        """
        # Get the opening times in the format that is expected by the DoS Service History Table
        opening_times = [
            specified_opening_time.export_service_history_format() for specified_opening_time in opening_times
        ]  # type: ignore
        return list(chain.from_iterable(opening_times))

    def save_service_histories(self, connection: connection) -> None:
        """Saves the service_histories json to the database

        Args:
            connection (connection): The database connection
        """
        # Generate the epoch time in seconds rounded down to the nearest second at the time of saving
        current_epoch_time = str(int(time()))
        # Get local datetime and format it to DoS date/time format
        current_date_time = datetime.now(timezone("Europe/London")).strftime("%Y-%m-%d %H:%M:%S")
        # Rename the new_change key to the current epoch time
        self.service_history[current_epoch_time] = self.service_history.pop("new_change")
        # Add the current time to the service_histories json
        self.service_history[current_epoch_time]["initiator"]["timestamp"] = current_date_time
        self.service_history[current_epoch_time]["approver"]["timestamp"] = current_date_time
        # Merge the new history changes into the existing history changes
        self.service_history |= self.existing_service_history
        logger.debug(f"Service history to be saved: {self.service_history}")
        cursor = query_dos_db(
            connection=connection,
            query=(
                f"""UPDATE services SET modifiedby='DOS_INTEGRATION', """
                f"""modifiedtime='{current_date_time}' WHERE id = '{self.service_id}';"""
            ),
        )
        cursor.close()
        if self.history_already_exists:
            # Update the service_histories json in the database
            cursor = query_dos_db(
                connection=connection,
                query=(
                    f"""UPDATE servicehistories SET history = {Json(self.service_history)} """
                    f"""WHERE serviceid = '{self.service_id}';"""
                ),
            )
            logger.info(f"Service history updated for serviceid {self.service_id}")
            cursor.close()
        else:
            # Create a new entry in the service_histories json for the service
            cursor = query_dos_db(
                connection=connection,
                query=(
                    """INSERT INTO servicehistories (serviceid, history) """
                    f"""VALUES ('{self.service_id}', {Json(self.service_history)});"""
                ),
            )
            cursor.close()
            logger.warning(f"Service history created in the database for serviceid {self.service_id}")
        cursor.close()
