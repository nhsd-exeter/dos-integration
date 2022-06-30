from pytest import fixture

from .utilities.context import Context


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


@fixture
def context(autouse=True):
    yield Context()
