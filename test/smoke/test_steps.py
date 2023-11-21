from datetime import datetime
from re import sub

import pytest
from faker import Faker
from pytest_bdd import given, scenarios, then, when
from pytz import timezone

from .functions.change_event import ChangeEvent
from .functions.change_event_request import send_change_event
from .functions.service import (
    check_blood_pressure_updated,
    check_contraception_updated,
    check_demographic_field_updated,
    check_specified_opening_times_updated,
    check_standard_opening_times_updated,
    get_change_event_for_service,
    wait_for_service_update,
)
from .functions.smoke_test_context import SmokeTestContext

scenarios("smoke.feature")
FAKER = Faker("en_GB")


@pytest.fixture()
def smoke_test_context() -> SmokeTestContext:
    """Set up the smoke test context."""
    return SmokeTestContext()


@given("I create a new change event matching DoS", target_fixture="smoke_test_context")
def _(smoke_test_context: SmokeTestContext) -> SmokeTestContext:
    """Create a new change event matching DoS.

    Args:
        smoke_test_context (SmokeTestContext): The smoke test context

    Returns:
        SmokeTestContext: The smoke test context
    """
    smoke_test_context.original_service = get_change_event_for_service("FC766")
    smoke_test_context.updated_service = ChangeEvent(
        address=smoke_test_context.original_service.address,
        website=smoke_test_context.original_service.website,
        phone=smoke_test_context.original_service.phone,
        standard_opening_times=smoke_test_context.original_service.standard_opening_times,
        specified_opening_times=smoke_test_context.original_service.specified_opening_times,
        blood_pressure=smoke_test_context.original_service.blood_pressure,
        contraception=smoke_test_context.original_service.contraception,
    )
    return smoke_test_context


@given("I make changes to the change event", target_fixture="smoke_test_context")
def _(smoke_test_context: SmokeTestContext) -> SmokeTestContext:
    """Update the change event field to new value.

    Args:
        smoke_test_context (SmokeTestContext): The smoke test context

    Returns:
        SmokeTestContext: The smoke test context
    """

    def update_address() -> None:
        new_address = f"{FAKER.street_address()}${FAKER.city()}"
        new_address = sub(r"[A-Za-z]+('[A-Za-z]+)?", lambda word: word.group(0).capitalize(), new_address)
        new_address = new_address.replace("\n", "$")
        new_address = new_address.replace("'", "")
        new_address = new_address.replace("&", "and")
        smoke_test_context.updated_service.address = new_address

    def update_website() -> None:
        smoke_test_context.updated_service.website = FAKER.url()

    def update_phone() -> None:
        smoke_test_context.updated_service.phone = FAKER.phone_number().replace(" ", "")

    def update_standard_opening_times() -> None:
        smoke_test_context.updated_service.standard_opening_times = [
            {
                "day": FAKER.day_of_week(),
                "open": "00:01",
                "close": FAKER.time(pattern="%H:%M", end_datetime=None),
                "open_or_closed": True,
            },
        ]

    def update_specified_opening_times() -> None:
        smoke_test_context.updated_service.specified_opening_times = [
            {
                "date": FAKER.date_this_year(before_today=False, after_today=True),
                "open": "09:00",
                "close": "17:00",
                "open_or_closed": True,
            },
        ]

    def update_blood_pressure() -> None:
        smoke_test_context.updated_service.blood_pressure = not smoke_test_context.updated_service.blood_pressure

    def update_contraception() -> None:
        smoke_test_context.updated_service.contraception = not smoke_test_context.updated_service.contraception

    update_address()
    update_website()
    update_phone()
    update_standard_opening_times()
    update_specified_opening_times()
    update_blood_pressure()
    update_contraception()

    return smoke_test_context


@given("I want to reset the change event", target_fixture="smoke_test_context")
def _(smoke_test_context: SmokeTestContext) -> SmokeTestContext:
    """Reset the change event to the original value.

    Args:
        smoke_test_context (SmokeTestContext): The smoke test context

    Returns:
        SmokeTestContext: The smoke test context
    """
    if not smoke_test_context.original_service.standard_opening_times:
        smoke_test_context.blank_opening_times = True
        smoke_test_context.original_service.standard_opening_times = (
            smoke_test_context.updated_service.standard_opening_times
        )
    smoke_test_context.updated_service = smoke_test_context.original_service
    return smoke_test_context


@when("I run the smoke test", target_fixture="smoke_test_context")
def _(smoke_test_context: SmokeTestContext) -> SmokeTestContext:
    """Run the smoke test.

    Args:
        smoke_test_context (SmokeTestContext): The smoke test context

    Returns:
        SmokeTestContext: The smoke test context
    """
    smoke_test_context.request_start_time = datetime.now(tz=timezone("Europe/London"))
    change_event_json = smoke_test_context.updated_service.create_change_event()
    send_change_event(change_event_json)
    return smoke_test_context


@then("I should see an update to DoS", target_fixture="smoke_test_context")
def _(smoke_test_context: SmokeTestContext) -> SmokeTestContext:
    """Check the DoS service has been updated.

    Args:
        smoke_test_context (SmokeTestContext): The smoke test context

    Returns:
        SmokeTestContext: The smoke test context
    """
    wait_for_service_update(smoke_test_context.request_start_time)
    return smoke_test_context


@then("I should see data matching the updated service in DoS")
@then("I should see data matching the original service in DoS")
def _(smoke_test_context: SmokeTestContext) -> None:
    """Check the DoS service has been updated to match the original service.

    Args:
        smoke_test_context (SmokeTestContext): The smoke test context

    Returns:
        SmokeTestContext: The smoke test context
    """
    check_demographic_field_updated(
        field="address",
        service_history_key="postaladdress",
        expected_value=smoke_test_context.updated_service.address,
    )
    check_demographic_field_updated(
        field="web",
        service_history_key="cmsurl",
        expected_value=smoke_test_context.updated_service.website,
    )
    check_demographic_field_updated(
        field="publicphone",
        service_history_key="cmstelephoneno",
        expected_value=smoke_test_context.updated_service.phone,
    )
    check_standard_opening_times_updated(
        expected_value=smoke_test_context.updated_service.standard_opening_times,
        smoke_test_context=smoke_test_context,
    )
    check_specified_opening_times_updated(expected_value=smoke_test_context.updated_service.specified_opening_times)
    check_blood_pressure_updated(expected_value=smoke_test_context.updated_service.blood_pressure)
    check_contraception_updated(expected_value=smoke_test_context.updated_service.contraception)
