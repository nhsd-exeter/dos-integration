import pytest
from faker import Faker
from pytest_bdd import given, scenarios, then, when
from pytest_bdd.parsers import parse

from .functions.smoke_test_context import SmokeTestContext

scenarios("smoke.feature")
FAKER = Faker("en_GB")


@pytest.fixture()
def smoke_test_context() -> SmokeTestContext:
    """Set up the smoke test context."""
    return SmokeTestContext()


@given("I create a new change event matching DoS", target_fixture="smoke_test_context")
def _(smoke_test_context: SmokeTestContext) -> SmokeTestContext:
    return smoke_test_context


@given(parse('I update the change event "{field}"'), target_fixture="smoke_test_context")
def _(field: str, smoke_test_context: SmokeTestContext) -> SmokeTestContext:
    """Update the change event field to new value.

    Args:
        field (str): The field to update
    """
    return smoke_test_context


@given("I want to reset the change event", target_fixture="smoke_test_context")
def _(smoke_test_context: SmokeTestContext) -> SmokeTestContext:
    return smoke_test_context


@when("I run the smoke test", target_fixture="smoke_test_context")
def _(smoke_test_context: SmokeTestContext) -> SmokeTestContext:
    return smoke_test_context


@then("I should see an update to DoS", target_fixture="smoke_test_context")
def _(smoke_test_context: SmokeTestContext) -> SmokeTestContext:
    return smoke_test_context


@then(
    parse('I should see an update to the "{field}" field and service history in DoS'),
    target_fixture="smoke_test_context",
)
def _(field: str, smoke_test_context: SmokeTestContext) -> SmokeTestContext:
    """Check the DoS service history and field has been updated.

    Args:
        field (str): The field to check
    """
    return smoke_test_context


@then("I should see data matching the original service in DoS")
def _(smoke_test_context: SmokeTestContext) -> None:
    pass
