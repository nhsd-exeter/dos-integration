from typing import Any, Self

from locust import FastHttpUser, task

from functions.api import send_change_event
from functions.change_event import ChangeEvent
from functions.utilities import get_api_key


class PerformanceTest(FastHttpUser):
    """This class is to run the performance test.

    This test runs like a stress test. Use a delay to control the rate of requests.
    """

    abstract = True
    headers: dict[str, str]
    payload: dict[str, Any]

    def on_start(self) -> None:
        """Get the api key before starting the test."""
        self.api_key = get_api_key()

    @task(3)
    def all_updates_change_event(self: Self) -> None:
        """Send an all changes change event.

        Args:
            self (Self): The class
        """
        change_event = ChangeEvent()
        change_event.cause_contact_updates()
        change_event.cause_location_updates()
        change_event.cause_opening_times_updates()
        change_event.cause_blood_pressure_updates()
        change_event.cause_contraception_updates()
        self.payload = change_event.create_change_event_json()
        send_change_event(request_name="AllChangesChangeEvent", request=self, valid_ods_code=True)

    @task
    def contact_updates_change_event(self: Self) -> None:
        """Send a contact change event.

        Args:
            self (Self): The class
        """
        change_event = ChangeEvent()
        change_event.cause_contact_updates()
        self.payload = change_event.create_change_event_json()
        send_change_event(request_name="ContactChangeEvent", request=self, valid_ods_code=True)

    @task
    def location_updates_change_event(self: Self) -> None:
        """Send a location change event.

        Args:
            self (Self): The class
        """
        change_event = ChangeEvent()
        change_event.cause_location_updates()
        self.payload = change_event.create_change_event_json()
        send_change_event(request_name="LocationChangeEvent", request=self, valid_ods_code=True)

    @task(2)
    def opening_times_updates_change_event(self: Self) -> None:
        """Send an opening times change event.

        Args:
            self (Self): The class
        """
        change_event = ChangeEvent()
        change_event.cause_opening_times_updates()
        self.payload = change_event.create_change_event_json()
        send_change_event(request_name="OpeningTimesChangeEvent", request=self, valid_ods_code=True)

    # Palliative care is not currently supported in the performance environments
    # @task
    # def palliative_care_changes_change_event(self: Self) -> None:
    #     """Send a palliative care change event.

    #     Args:
    #         self (Self): The class
    #     """

    @task
    def blood_pressure_updates_change_event(self: Self) -> None:
        """Send a blood pressure change event.

        Args:
            self (Self): The class
        """
        change_event = ChangeEvent()
        change_event.cause_blood_pressure_updates()
        self.payload = change_event.create_change_event_json()
        send_change_event(request_name="BloodPressureChangeEvent", request=self, valid_ods_code=True)

    @task
    def contraception_updates_change_event(self: Self) -> None:
        """Send a contraception change event.

        Args:
            self (Self): The class
        """
        change_event = ChangeEvent()
        change_event.cause_contraception_updates()
        self.payload = change_event.create_change_event_json()
        send_change_event(request_name="ContraceptionChangeEvent", request=self, valid_ods_code=True)

    @task
    def no_match_change_event(self: Self) -> None:
        """Send a no match change event.

        Args:
            self (Self): The class
        """
        change_event = ChangeEvent()
        self.payload = change_event.create_change_event_json()
        send_change_event(request_name="NoMatchChangeEvent", request=self, valid_ods_code=False)
