from behave import given, then, when
from time import sleep, time
from json import dumps
from base64 import b64encode
from features.utilities.encryption import initialise_encryption_client
from features.utilities.utils import (
    get_lambda_info,
    process_payload,
    get_stored_events_from_dynamo_db,
    search_dos_db,
    process_change_request_payload,
)
from decimal import Decimal
from features.utilities.changed_events import changed_event
from features.utilities.log_stream import get_logs
from datetime import datetime
# import sys
# sys.path.append('application/common/aws.py')
# from application.common.aws import get_secret


@given("a Changed Event is valid")
def a_change_event_is_valid(context):
    context.change_event = changed_event()


@given("a valid unsigned change request")
def a_change_request_is_valid(context):
    context.change_request = get_change_request()


@given("a Changed Event with invalid ODSCode is provided")
def a_change_event_with_invalid_odscode(context):
    context.change_event = changed_event()
    context.change_event["ODSCode"] = "F8KE1"


@given("change request has valid signature")
def has_valid_signature(context):
    key_data = {
        "ods_code": context.change_request["ods_code"],
        "dynamo_record_id": context.change_request["dynamo_record_id"],
        "message_received": context.change_request["message_received"],
        "time": time(),
    }
    encrypt_string = initialise_encryption_client()
    signing_key = encrypt_string(dumps(key_data))
    b64_mystring = b64encode(signing_key).decode("utf-8")
    context.change_request["signing_key"] = b64_mystring


@given("change request has invalid signature")
def has_invalid_signature(context):
    key_data = {
        "ods_code": "Dave",
        "dynamo_record_id": context.change_request["dynamo_record_id"],
        "message_received": context.change_request["message_received"],
        "time": time(),
    }
    encrypt_string = initialise_encryption_client()
    signing_key = encrypt_string(dumps(key_data))
    b64_mystring = b64encode(signing_key).decode("utf-8")
    context.change_request["signing_key"] = b64_mystring


@given("change request has expired signature")
def has_expired_signature(context):
    key_data = {
        "ods_code": "Dave",
        "dynamo_record_id": context.change_request["dynamo_record_id"],
        "message_received": context.change_request["message_received"],
        "time": time() - 100_000,
    }
    encrypt_string = initialise_encryption_client()
    signing_key = encrypt_string(dumps(key_data))
    b64_mystring = b64encode(signing_key).decode("utf-8")
    context.change_request["signing_key"] = b64_mystring

@given("a Changed Event contains an incorrect OrganisationSubType")
def a_change_event_with_invalid_organisationsubtype(context):
    context.change_event = changed_event()
    context.change_event["OrganisationSubType"] = "com"


@given("a Changed Event contains an incorrect OrganisationTypeID")
def a_change_event_with_invalid_organisationtypeid(context):
    context.change_event = changed_event()
    context.change_event["OrganisationTypeId"] = "DEN"


@when('the Changed Event is sent for processing with "{valid_or_invalid}" api key')
def the_change_event_is_sent_for_processing(context, valid_or_invalid):
    context.start_time = datetime.today().timestamp()
    context.response = process_payload(context.change_event, valid_or_invalid == "valid")
    context.correlation_id = context.response.headers["x-amz-apigw-id"]
    context.sequence_no = context.response.request.headers["sequence-number"]


@when('the change request is sent with "{valid_or_invalid}" api key')
def the_change_request_is_sent(context, valid_or_invalid):

    context.start_time = datetime.today().timestamp()
    context.response = process_change_request_payload(context.change_request, valid_or_invalid == "valid")


@then('the change request has status code "{status}"')
def step_then_should_transform_into(context, status):
    print(context.response)
    message = context.response.json
    assert (
        str(context.response.status_code) == status
    ), f"Status code not as expected: {context.response.status_code} != {status} Error: {message} - {status}"


# When the postcode has no LAT/Long values
@when('the postcode has no LAT/Long values')
def postcode_with_no_lat_long_values(context):
    context.change_event["Postcode"] = "BT4 2HU"

# When the OrganisationStatus is equal to "Hidden" OR "Closed"
@when('the OrganisationStatus is defined as {org_status}')
def a_change_event_with_orgstatus_value(context, org_status: str):
    context.change_event["OrganisationStatus"] = org_status


# When the postcode is invalid
@when('the postcode is invalid')
def postcode_is_invalid(context):
    context.change_event["Postcode"] = "AAAA 123"


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

@then("the exception is reported to cloudwatch")
def service_exception(context):
    query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context.correlation_id}"'
        ' | filter level="ERROR"'
    )
    logs = get_logs(query, "processor", context.start_time)
    assert logs != [], "ERROR!!.. Expected exception not logged."

@then("the invalid postcode exception is reported to cloudwatch")
def unmatched_postcode_exception(context):
    query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context.correlation_id}"'
        ' | filter message like "is not a valid DoS postcode"'
    )
    logs = get_logs(query, "processor", context.start_time)
    postcode = context.change_event["Postcode"]
    assert f"postcode '{postcode}'" in logs, "ERROR!!.. Expected unmatched service logs not found."


@then("the hidden or closed exception is reported to cloudwatch")
def hidden_or_closed_exception(context):
    query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context.correlation_id}"'
        ' | filter message like "NHS Service marked as closed or hidden"'
    )
    logs = get_logs(query, "processor", context.start_time)
    assert "no change requests will be produced" in logs, "ERROR!!.. Expected unmatched service logs not found."

@then("the address change is not included in the change request")
def address_change_is_discarded_in_event_proc(context):
    query = (
        f'fields message | sort @timestamp asc | filter correlation_id="{context.correlation_id}"'
        ' | filter message like "Deleted address change as postcode is invalid"'
    )
    logs = get_logs(query, "processor", context.start_time)
    assert "postcode is invalid" in logs, "ERROR!!.. Expected unmatched service logs not found."

@then("the event sender does not contain address changes")
def address_change_is_discarded_in_event_sender(context):
    query = (
        f'fields change_request_body | sort @timestamp asc | filter correlation_id="{context.correlation_id}"'
        ' | filter message like "Attempting to send change request to DoS"'
    )
    logs = get_logs(query, "sender", context.start_time)
    assert "postcode" not in logs, "ERROR!!.. Expected unmatched service logs not found."


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
    assert f"{cr_received_search_param}" not in logs, "ERROR!!.. expected exception logs not found."


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
