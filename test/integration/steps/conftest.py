from pytest import fixture

from .utilities.context import Context
from .utilities.generator import set_up_palliative_care_in_db


def log_test_summary(step, request):
    print(f"Step Summary: For {step}")
    try:
        print(request.getfixturevalue("context"))
    except Exception:
        print("No context")


def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception):
    log_test_summary(step, request)


def pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args):
    log_test_summary(step, request)


@fixture()
def context(autouse=True):
    return Context()


def pytest_sessionstart(session):
    """Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    set_up_palliative_care_in_db()
