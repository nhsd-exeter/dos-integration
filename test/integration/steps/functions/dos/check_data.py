from typing import Any

from integration.steps.functions.aws.aws_lambda import invoke_dos_db_handler_lambda
from integration.steps.functions.utils import check_recent_event

from .get_data import get_service_history
from .translation import get_service_history_data_key


def check_pending_service_is_rejected(service_id: str) -> Any:
    """Check pending service is rejected.

    Args:
        service_id (str): Service id.

    Returns:
        Any: Pending service is rejected.
    """
    query = "SELECT approvestatus FROM changes WHERE serviceid = %(SERVICE_ID)s"
    query_vars = {"SERVICE_ID": service_id}
    lambda_payload = {"type": "read", "query": query, "query_vars": query_vars}
    return invoke_dos_db_handler_lambda(lambda_payload)


def check_service_history(
    service_id: str,
    plain_english_field_name: str,
    expected_data: Any,
    previous_data: Any,
) -> None:
    """Check the service history for the expected data and previous data is removed."""
    service_history = get_service_history(service_id)
    first_key_in_service_history = next(iter(service_history.keys()))
    changes = service_history[first_key_in_service_history]["new"]
    change_key = get_service_history_data_key(plain_english_field_name)
    if change_key not in changes:
        msg = f"DoS Change key '{change_key}' not found in latest service history entry"
        raise ValueError(msg)

    assert (
        expected_data == changes[change_key]["data"]
    ), f"Expected data: {expected_data}, Expected data type: {type(expected_data)}, Actual data: {changes[change_key]['data']}"  # noqa: E501

    if "previous" in changes[change_key] and previous_data != "unknown":
        if previous_data != "":  # noqa: PLC1901, RUF100
            assert changes[change_key]["previous"] == str(
                previous_data,
            ), f"Expected previous data: {previous_data}, Actual data: {changes[change_key]}"
        else:
            assert (
                changes[change_key]["previous"] is None
            ), f"Expected previous data: {previous_data}, Actual data: {changes[change_key]}"


def service_history_negative_check(service_id: str) -> str:
    """Check the service history for the expected data and previous data is removed.

    Args:
        service_id (str): Service ID of the service to be checked

    Returns:
        str: Returns a string based on the result of the check
    """
    service_history = get_service_history(service_id)
    if service_history == []:
        return "Not Updated"

    first_key_in_service_history = next(iter(service_history.keys()))
    if check_recent_event(first_key_in_service_history) is False:
        return "Not Updated"
    return "Updated"


def check_service_history_change_type(service_id: str, change_type: str, field_name: None | str = None) -> str:
    """Check the service history for the expected change type.

    Args:
        service_id (str): Service ID of the service to be checked
        change_type (str): Change type to be checked
        field_name (str, optional): Field to search for in history. Defaults to None.

    Returns:
        str: Returns a string based on the result of the check
    """
    service_history = get_service_history(service_id)
    first_key_in_service_history = next(iter(service_history.keys()))
    if field_name is None:
        change_status = service_history[first_key_in_service_history]["new"][
            next(iter(service_history[first_key_in_service_history]["new"].keys()))
        ]["changetype"]
    else:
        change_status = service_history[first_key_in_service_history]["new"][field_name]["changetype"]
    if check_recent_event(first_key_in_service_history):
        if change_status == change_type or change_type == "modify" and change_status == "add":
            return "Change type matches"
        return "Change type does not match"
    return "No changes have been made"
