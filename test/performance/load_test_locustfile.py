from typing import Self

from locust import constant_pacing, task

from functions.api import send_change_event
from functions.change_event import ChangeEvent
from functions.dos_integration_fast_http_user import DoSIntegrationFastHttpUser


class AllChangesChangeEvent(DoSIntegrationFastHttpUser):
    """This class is to send a change event with all changes."""

    weight = 3
    wait_time = constant_pacing(10)

    @task
    def change_event(self: Self) -> None:
        """Send a change event.

        Args:
            self (Self): The class
        """
        change_event = ChangeEvent()
        change_event.cause_contact_updates()
        change_event.cause_location_updates()
        change_event.cause_opening_times_updates()
        change_event.cause_palliative_care_updates()
        change_event.cause_blood_pressure_updates()
        change_event.cause_contraception_updates()
        self.payload = change_event.create_change_event_json()
        send_change_event(request_name="AllChangesChangeEvent", request=self, valid_ods_code=True)


class ContactChangeEvent(DoSIntegrationFastHttpUser):
    """This class is to send a change event with contact changes."""

    weight = 1
    wait_time = constant_pacing(10)

    @task
    def change_event(self: Self) -> None:
        """Generates and sends a change event.

        Args:
            self (Self): The class
        """
        change_event = ChangeEvent()
        change_event.cause_contact_updates()
        self.payload = change_event.create_change_event_json()
        send_change_event(request_name="ContactChangeEvent", request=self, valid_ods_code=True)


class LocationChangeEvent(DoSIntegrationFastHttpUser):
    """This class is to send a change event with location changes."""

    weight = 1
    wait_time = constant_pacing(10)

    @task
    def change_event(self: Self) -> None:
        """Generates and sends a change event.

        Args:
            self (Self): The class
        """
        change_event = ChangeEvent()
        change_event.cause_location_updates()
        self.payload = change_event.create_change_event_json()
        send_change_event(request_name="LocationChangeEvent", request=self, valid_ods_code=True)


class OpeningTimesChangeEvent(DoSIntegrationFastHttpUser):
    """This class is to send a change event with opening times changes."""

    weight = 1
    wait_time = constant_pacing(10)

    @task
    def change_event(self: Self) -> None:
        """Generates and sends a change event.

        Args:
            self (Self): The class
        """
        change_event = ChangeEvent()
        change_event.cause_opening_times_updates()
        self.payload = change_event.create_change_event_json()
        send_change_event(request_name="OpeningTimesChangeEvent", request=self, valid_ods_code=True)


class PalliativeCareChangeEvent(DoSIntegrationFastHttpUser):
    """This class is to send a change event with palliative care changes."""

    weight = 1
    wait_time = constant_pacing(10)

    @task
    def change_event(self: Self) -> None:
        """Generates and sends a change event.

        Args:
            self (Self): The class
        """
        change_event = ChangeEvent()
        change_event.cause_palliative_care_updates()
        self.payload = change_event.create_change_event_json()
        send_change_event(request_name="PalliativeCareChangeEvent", request=self, valid_ods_code=True)


class BloodPressureChangeEvent(DoSIntegrationFastHttpUser):
    """This class is to send a change event with blood pressure changes."""

    weight = 1
    wait_time = constant_pacing(10)

    @task
    def change_event(self: Self) -> None:
        """Generates and sends a change event.

        Args:
            self (Self): The class
        """
        change_event = ChangeEvent()
        change_event.cause_blood_pressure_updates()
        self.payload = change_event.create_change_event_json()
        send_change_event(request_name="BloodPressureChangeEvent", request=self, valid_ods_code=True)


class ContraceptionChangeEvent(DoSIntegrationFastHttpUser):
    """This class is to send a change event with contraception changes."""

    weight = 1
    wait_time = constant_pacing(10)

    @task
    def change_event(self: Self) -> None:
        """Generates and sends a change event.

        Args:
            self (Self): The class
        """
        change_event = ChangeEvent()
        change_event.cause_contraception_updates()
        self.payload = change_event.create_change_event_json()
        send_change_event(request_name="ContraceptionChangeEvent", request=self, valid_ods_code=True)


class NoMatchChangeEvent(DoSIntegrationFastHttpUser):
    """This class is to s end a change event with no match."""

    weight = 1
    wait_time = constant_pacing(10)

    @task
    def change_event(self: Self) -> None:
        """Generates and sends a change event.

        Args:
            self (Self): The class
        """
        change_event = ChangeEvent()
        self.payload = change_event.create_change_event_json()
        send_change_event(request_name="NoMatchChangeEvent", request=self, valid_ods_code=False)
