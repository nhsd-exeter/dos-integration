import pytest

from .utilities.context import Context
from .utilities.generator import set_up_common_condition_service_types, set_up_palliative_care_in_db


def log_test_summary(step, request) -> None:
    """Log test summary."""
    print(f"Step Summary: For {step}")
    try:
        print(request.getfixturevalue("context"))
    except Exception:
        print("No context")


def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception) -> None:
    """Called after a step function raised an exception."""
    log_test_summary(step, request)


def pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args) -> None:
    """Called after a step function call."""
    log_test_summary(step, request)


@pytest.fixture(autouse=True)
def context() -> Context:
    """Fixture to create a context object for each test.

    Returns:
        Context: Context object.
    """
    return Context()


def pytest_sessionstart(session) -> None:
    """Called after the Session object has been created and before performing collection and entering the run test loop."""  # noqa: E501
    set_up_palliative_care_in_db()
    set_up_common_condition_service_types()
