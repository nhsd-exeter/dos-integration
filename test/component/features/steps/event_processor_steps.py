from os import getenv

from behave import given, then, when
from features.utilities.utilities import load_json_file, read_log_file
from requests import post
from json import dumps


@given("a change event that is for a service is the different from a DoS service")
def a_change_event_that_is_for_a_service_is_the_different_from_a_dos_service(context):
    context.change_event = load_json_file("event_processor_change_event_different_from_dos.json")


@given("a change event that is for a service is the same as a DoS service")
def a_change_event_that_is_for_a_service_is_the_same_as_a_dos_service(context):
    context.change_event = load_json_file("event_processor_change_event_same_as_dos.json")


@given("a change event for a service that doesn't exist in DoS")
def the_change_event_for_a_service_that_does_not_exist_in_dos(context):
    context.change_event = load_json_file("event_processor_change_event_different_from_dos.json")
    context.change_event["ODSCode"] = "FXXX1"  # Not in DoS


@when("the change event is sent to the event processor")
def the_change_event_is_sent_to_the_event_processor(context):
    """Sends change event to Event Processor lambda"""
    lambda_url = getenv("EVENT_PROCESSOR_FUNCTION_URL")
    context.response = post(url=lambda_url, headers={"Content-Type": "application/json"}, json=context.change_event)
    assert context.response.status_code == 200, "Lambda emulator didn't accept request"


@then("the change event that is for a service is different from a DoS service is logged")
def the_change_event_that_is_for_a_service_is_different_from_a_dos_service_is_logged(context):
    log_file = read_log_file()
    with open("features/resources/event_processor_change_event_different_from_dos.json", "r", encoding="utf-8") as file:
        expected_event = file.read()
    assert expected_event in log_file, "Change Event was not logged  which is different from dos"


@then("the change event that is for a service is the same as a DoS service")
def the_change_event_that_is_for_a_service_is_the_same_as_a_dos_service_is_logged(context):
    log_file = read_log_file()
    with open("features/resources/event_processor_change_event_same_as_dos.json", "r", encoding="utf-8") as file:
        expected_event = file.read()
    assert expected_event in log_file, "Change Event was not logged which is the same as dos"


@then("the change event for a service that doesn't exist in DoS is logged")
def the_change_event_for_a_service_that_does_not_exist_in_dos_is_logged(context):
    log_file = read_log_file()
    with open("features/resources/event_processor_change_event_different_from_dos.json", "r", encoding="utf-8") as file:
        expected_event = file.read()
    expected_event = expected_event.replace("FQ038", "FXXX1")
    assert expected_event in log_file, "Change Event was not logged which doesn't exist in DoS"


@then("the change request is produced and logged")
def the_change_request_is_produced_and_logged(context):
    log_file_contents = read_log_file()
    change_event = context.change_event
    expected_change_request = [
        {
            "reference": "<NO-TRACE-ID>",
            "system": "DoS Integration",
            "message": "DoS Integration CR. AMZN-trace-id: <NO-TRACE-ID>",
            "service_id": "22899",
            "changes": {
                "website": change_event["Website"],
                "postcode": change_event["Postcode"],
                "phone": change_event["Phone"],
                "public_name": change_event["OrganisationName"],
                "address": [
                    change_event["Address1"],
                    change_event["Address2"],
                    change_event["Address3"],
                    change_event["City"],
                    change_event["County"],
                ],
            },
        }
    ]
    expected_change_request = dumps(expected_change_request, indent=2, default=str)
    assert (
        expected_change_request in log_file_contents
    ), f"Change Request was not logged, {expected_change_request=} {log_file_contents=}"


@then("no change request is produced")
def the_change_request_is_produced(context):
    log_file_contents = read_log_file()
    expected_change_request_message = "|Created 0 change requests []"
    assert (
        expected_change_request_message in log_file_contents
    ), f"Change Request count message was not logged, {expected_change_request_message=}"
