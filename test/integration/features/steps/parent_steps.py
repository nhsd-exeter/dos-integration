from behave import given, then, when
from time import sleep
from features.utilities.utils import (
    get_lambda_info,
    process_payload,
    get_stored_events_from_dynamo_db,
    search_dos_db,
)
from decimal import Decimal
from features.utilities.change_events import get_change_event, random_odscode
from features.utilities.log_stream import get_logs
from datetime import datetime


@given("a Changed Event is valid")
def a_change_event_is_valid(context):
    """Creates a valid change event"""
    context.change_event = get_change_event()
    context.change_event["ODSCode"] = random_odscode()


@given("a Changed Event with invalid ODSCode is provided")
def a_change_event_with_invalid_odscode(context):
    """Creates a valid change event"""
    context.change_event = get_change_event()
    context.change_event["ODSCode"] = "F8KE1"


@given("a Changed Event with invalid OrganisationSubType is provided")
def a_change_event_with_invalid_organisationsubtype(context):
    """Creates a valid change event"""
    context.change_event = get_change_event()
    context.change_event["OrganisationSubType"] = "com"


@given("a Changed Event with invalid OrganisationTypeID is provided")
def a_change_event_with_invalid_organisationtypeid(context):
    """Creates a valid change event"""
    context.change_event = get_change_event()
    context.change_event["OrganisationTypeID"] = "DEN"


@when("the Changed Event is sent for processing")
def the_change_event_is_sent_for_processing(context):
    context.start_time = datetime.today().timestamp()
    context.response = process_payload(context.change_event)
    context.correlation_id = context.response.headers["x-amz-apigw-id"]
    context.sequence_no = context.response.request.headers["sequence-number"]
    message = context.response.json()
    assert (
        context.response.status_code == 200
    ), f"Status code not as expected.. Status code: {context.response.status_code} Error: {message}"


@then("no matched services were found")
def no_matched_services_found(context):
    query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context.correlation_id}"'
        ' | filter message like "Found 0 services in DB"'
    )
    event_logs = get_logs(query, "processor", context.start_time)
    assert event_logs != [], "ERROR!! No unmatched services log found.."


@then('the "{event}" logs are generated')
def the_lambda_logs_are_generated(context, event: str):
    query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context.correlation_id}"',
        ' | filter message="Event has been validated"',
    )
    event_logs = get_logs(query, event, context.start_time)
    assert event_logs != [], "ERROR!! No logs found!.."


@then("the Changed Event is stored in dynamo db")
def stored_dynamo_db_events_are_pulled(context):
    sleep(3)
    odscode = context.change_event["ODSCode"]
    sequence_num = Decimal(context.sequence_no)
    db_event_record = get_stored_events_from_dynamo_db(odscode, sequence_num)
    assert db_event_record is not None, f"ERROR!! Event record with odscode {odscode} NOT found!.."
    assert (
        odscode == db_event_record["ODSCode"]
    ), f"ERROR!!.. Change event record({odscode} - {db_event_record['ODSCode']}) mismatch!!"
    assert sequence_num == db_event_record["SequenceNumber"], "ERROR!!.. Change event record(sequence no) mismatch!!"


@then("the lambda is confirmed active")
def the_lambda_is_confirmed_active(context):
    status = get_lambda_info("status")
    assert status == "Active" or "Successful", "ERROR! Invocation either unsuccessful or Lambda is inactive"


@then("the Changed Event is processed")
def the_changed_event_is_processed(context):
    search_param = "Sent off change payload"
    query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context.correlation_id}"'
        f' | filter message like "{search_param}"'
    )
    logs = get_logs(query, "processor", context.start_time)
    assert logs != [], "ERROR!!.. logs not found"


@then("the unmatched service exception is reported to cloudwatch")
def unmatched_service_exception(context):
    query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context.correlation_id}"'
        ' | filter message like "No matching DOS services"'
    )
    logs = get_logs(query, "processor", context.start_time)
    odscode = context.change_event["ODSCode"]
    assert f"ODSCode '{odscode}'" in logs, "ERROR!!.. Expected unmatched service logs not found."


@then("the processed Changed Request is sent to Dos")
def processed_changed_request_sent_to_dos(context):
    cr_received_search_param = "Received change request"
    cr_sent_search_param = "Successfully send change request to DoS"
    cr_received_query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context.correlation_id}"'
        f' | filter message like "{cr_received_search_param}"'
    )
    cr_sent_query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context.correlation_id}"'
        f' | filter message like "{cr_sent_search_param}"'
    )
    cr_received_logs = get_logs(cr_received_query, "sender", context.start_time)
    assert cr_received_logs != [], "ERROR!!.. Expected Sender logs not found."
    cr_sent_logs = get_logs(cr_sent_query, "sender", context.start_time)
    assert cr_sent_logs != [], "ERROR!!.. Expected sent event confirmation in service logs not found."


@then("the Changed Event is not processed any further")
def the_changed_event_is_not_processed(context):
    cr_received_search_param = "Received change request"
    query = f'fields message | sort @timestamp asc | filter correlation_id="{context.correlation_id}"'
    logs = get_logs(query, "processor", context.start_time)
    assert f"{cr_received_search_param}" not in logs, "ERROR!!.. expected unmatched service logs not found."


# The below step definition answers to a corresponding 'AND' annotation within the feature file
@then("the Changed Request is accepted by Dos")
def the_changed_request_is_accepted_by_dos(context):
    """assert dos API response and validate processed record in Dos CR Queue database"""
    query = f"select value from changes where externalref = '{context.correlation_id}'"
    response = search_dos_db(query)
    assert response != [], "ERROR!!.. Expected Event confirmation in Dos not found."


@then("the Changed Event is not sent to Dos")
def the_changed_event_is_not_sent_to_dos(context):
    query = "select * from changes"
    response = search_dos_db(query)
    assert context.correlation_id not in response, "ERROR!!.. Event data found in Dos."
