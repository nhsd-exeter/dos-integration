def log_test_summary(step, request) -> None:
    """Log test summary."""
    print(f"Step Summary: For {step}")
    try:
        print(request.getfixturevalue("smoke_test_context"))
    except Exception:
        print("No smoke_test_context")


def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception) -> None:
    """Called after a step function raised an exception."""
    log_test_summary(step, request)


def pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args) -> None:
    """Called after a step function call."""
    log_test_summary(step, request)
