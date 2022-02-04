from datetime import datetime

from pytest_bdd import given, parsers, then, when

from .utilities.changed_events import change_request
from .utilities.utils import (
    process_change_request_payload,
)


@given("a valid unsigned change request", target_fixture="context")
def a_change_request_is_valid():
    context = {}
    context["change_request"] = change_request()
    return context


@when(parsers.parse('the change request is sent with "{valid_or_invalid}" api key'), target_fixture="context")
def the_change_request_is_sent(context, valid_or_invalid):
    context["start_time"] = datetime.today().timestamp()
    context["response"] = process_change_request_payload(context.change_request, valid_or_invalid == "valid")
    return context


@then(parsers.parse('the change request has status code "{status}"'))
def step_then_should_transform_into(context, status):
    message = context["response"].json
    assert (
        str(context["response"].status_code) == status
    ), f'Status code not as expected: {context["response"].status_code} != {status} Error: {message} - {status}'
