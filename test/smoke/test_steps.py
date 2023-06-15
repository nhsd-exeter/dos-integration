from faker import Faker
from pytest_bdd import given, scenarios, then, when
from pytest_bdd.parsers import parse

scenarios("smoke.feature")
FAKER = Faker("en_GB")


@given("I create a new change event matching DoS")
def _() -> None:
    pass


@given(parse('I update the change event "{field}"'))
def _(field: str) -> None:
    """Update the change event field to new value.

    Args:
        field (str): The field to update
    """


@given("I want to reset the change event")
def _() -> None:
    pass


@when("I run the smoke test")
def _() -> None:
    pass


@then("I should see an update to DoS")
def _() -> None:
    pass


@then(parse('I should see an update to the "{field}" field and service history in DoS'))
def _(field: str) -> None:
    """Check the DoS service history and field has been updated.

    Args:
        field (str): The field to check
    """


@then("I should see data matching the original service in DoS")
def _() -> None:
    pass
