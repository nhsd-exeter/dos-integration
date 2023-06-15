from datetime import datetime
from json import loads
from time import sleep

from pytz import UTC

from .aws import invoke_dos_db_handler_lambda
from .change_event import ChangeEvent
from .types import Demographics


def get_change_event_for_service(ods_code: str) -> ChangeEvent:
    """Get a service from DoS.

    Args:
        ods_code (str): The ODS code of the service to get
    """
    service_id = get_service_id_for_ods_code(ods_code)
    demographics = get_demographics_for_service(service_id)
    standard_opening_times = get_standard_opening_times_for_service(service_id)
    specified_opening_times = get_specified_opening_times_for_service(service_id)

    return ChangeEvent(
        address=demographics["address"],
        website=demographics["website"],
        phone=demographics["phone"],
        standard_opening_times=standard_opening_times,
        specified_opening_times=specified_opening_times,
    )


def get_service_id_for_ods_code(ods_code: str) -> str:
    """Get the service ID for an ODS code.

    Args:
        ods_code (str): The ODS code to get the service ID for

    Returns:
        str: The service ID for the ODS code
    """
    query = "SELECT id FROM services WHERE odscode = %(ODS_CODE)s"
    response = invoke_dos_db_handler_lambda({"type": "read", "query": query, "query_vars": {"ODS_CODE": ods_code}})
    response = loads(loads(response))
    return response[0]["id"]


def get_demographics_for_service(service_id: str) -> Demographics:
    """Get the demographics for a service.

    Args:
        service_id (str): The service ID to get the demographics for

    Returns:
        Demographics: The demographics for the service
    """
    query = "SELECT address, web, publicphone FROM services WHERE id = %(SERVICE_ID)s"
    response = invoke_dos_db_handler_lambda({"type": "read", "query": query, "query_vars": {"SERVICE_ID": service_id}})
    response_list = loads(loads(response))
    response_dict = response_list[0]
    return {
        "address": response_dict["address"],
        "website": response_dict["web"],
        "phone": response_dict["publicphone"],
    }


def get_standard_opening_times_for_service(service_id: str) -> dict:
    """Get the standard opening times for a service.

    Args:
        service_id (str): The service ID to get the standard opening times for

    Returns:
        dict: The standard opening times for the service
    """
    response = invoke_dos_db_handler_lambda({"type": "change_event_standard_opening_times", "service_id": service_id})
    return loads(response)


def get_specified_opening_times_for_service(service_id: str) -> dict:
    """Get the specified opening times for a service.

    Args:
        service_id (str): The service ID to get the specified opening times for

    Returns:
        dict: The specified opening times for the service
    """
    response = invoke_dos_db_handler_lambda({"type": "change_event_specified_opening_times", "service_id": service_id})
    return loads(response)


def get_service_history(service_id: str) -> dict:
    """Get the service history for a service.

    Args:
        service_id (str): The service ID to get the service history for

    Returns:
        dict: The service history for the service
    """


def get_service_modified_time(service_id: str) -> str:
    """Get the modifiedtime for a service.

    Args:
        service_id (str): The service ID to get the modifiedtime for

    Returns:
        str: The modifiedtime for the service
    """
    query = "SELECT modifiedtime FROM services WHERE id = %(SERVICE_ID)s"
    response = invoke_dos_db_handler_lambda({"type": "read", "query": query, "query_vars": {"SERVICE_ID": service_id}})
    response = loads(loads(response))
    return response[0]["modifiedtime"]


def wait_for_service_update(response_start_time: datetime) -> None:
    """Wait for the service to be updated by checking modifiedtime.

    Args:
        response_start_time (datetime): The time the response was started
    """
    service_id = get_service_id_for_ods_code("FC766")
    updated_date_time = None
    for _ in range(12):
        sleep(10)
        updated_date_time_str: str = get_service_modified_time(service_id)
        updated_date_time = datetime.strptime(updated_date_time_str, "%Y-%m-%d %H:%M:%S%z")
        updated_date_time = updated_date_time.replace(tzinfo=UTC)
        response_start_time = response_start_time.replace(tzinfo=UTC)
        if updated_date_time > response_start_time:
            break
    else:
        msg = f"Service not updated, service_id: {service_id}, modifiedtime: {updated_date_time}"
        raise ValueError(msg)


def check_demographic_field_updated(field: str, expected_value: str) -> None:
    """Check that the demographic field was updated."""
    service_id = get_service_id_for_ods_code("FC766")
    query = f"SELECT {field} FROM services WHERE id = %(SERVICE_ID)s"  # noqa: S608
    response = invoke_dos_db_handler_lambda({"type": "read", "query": query, "query_vars": {"SERVICE_ID": service_id}})
    response = loads(loads(response))
    assert (
        response[0][field] == expected_value
    ), f"Demographic field {field} was not updated - expected: '{expected_value}', actual: '{response[0][field]}'"
