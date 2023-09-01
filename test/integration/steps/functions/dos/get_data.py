from ast import literal_eval
from datetime import datetime, timedelta
from json import loads
from time import sleep
from typing import Any

from pytz import UTC, timezone

from integration.steps.functions.aws.aws_lambda import invoke_dos_db_handler_lambda


def wait_for_service_update(service_id: str) -> Any:
    """Wait for the service to be updated by checking modifiedtime."""
    for _ in range(12):
        sleep(10)
        updated_date_time_str: str = get_service_table_field(service_id, "modifiedtime")
        updated_date_time = datetime.strptime(updated_date_time_str, "%Y-%m-%d %H:%M:%S%z")
        updated_date_time = updated_date_time.replace(tzinfo=UTC)
        two_mins_ago = datetime.now(tz=timezone("Europe/London")) - timedelta(minutes=2)
        two_mins_ago = two_mins_ago.replace(tzinfo=UTC)
        if updated_date_time > two_mins_ago:
            break
    else:
        msg = f"Service not updated, service_id: {service_id}"
        raise ValueError(msg)


def get_locations_table_data(postcode: str) -> list:
    """Get locations table data.

    Args:
        postcode (str): Postcode to search for in locations table.

    Returns:
        list: Locations table data.
    """
    query = (
        "SELECT postaltown as town, postcode, easting, northing, latitude, longitude "
        "FROM locations WHERE postcode = %(POSTCODE)s"
    )
    query_vars = {"POSTCODE": postcode}
    lambda_payload = {"type": "read", "query": query, "query_vars": query_vars}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    return loads(loads(response))


def get_services_table_location_data(service_id: str) -> list:
    """Get services table location data.

    Args:
        service_id (str): Service id to search for in services table.

    Returns:
        list: Services table location data.
    """
    query = "SELECT town, postcode, easting, northing, latitude, longitude FROM services WHERE id = %(SERVICE_ID)s"
    query_vars = {"SERVICE_ID": service_id}
    lambda_payload = {"type": "read", "query": query, "query_vars": query_vars}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    return loads(loads(response))


def get_service_id(odscode: str) -> str:
    """Get service id.

    Args:
        odscode (str): ODSCode.

    Returns:
        str: Service id.
    """
    data = []
    query = f"SELECT id FROM services WHERE typeid = 13 AND statusid = 1 AND odscode like '{odscode}%' LIMIT 1"  # noqa: S608,E501
    for _ in range(16):
        lambda_payload = {"type": "read", "query": query, "query_vars": None}
        response = invoke_dos_db_handler_lambda(lambda_payload)
        data = loads(response)
        data = literal_eval(data)
        if data != []:
            break
        sleep(30)
    else:
        msg = "Error!.. Service Id not found"
        raise ValueError(msg)
    return data[0]["id"]


def get_change_event_standard_opening_times(service_id: str) -> Any:
    """Get change event standard opening times.

    Args:
        service_id (str): Service id.

    Returns:
        Any: Change event standard opening times.
    """
    lambda_payload = {"type": "change_event_standard_opening_times", "service_id": service_id}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    return loads(response)


def get_change_event_specified_opening_times(service_id: str) -> Any:
    """Get change event specified opening times.

    Args:
        service_id (str): Service id.

    Returns:
        Any: Change event specified opening times.
    """
    lambda_payload = {"type": "change_event_specified_opening_times", "service_id": service_id}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    return loads(response)


def get_service_table_field(service_id: str, field_name: str) -> Any:
    """Get service table field.

    Args:
        service_id (str): Service id.
        field_name (str): Field name.

    Returns:
        Any: Service table field.
    """
    query = f"SELECT {field_name} FROM services WHERE id = %(SERVICE_ID)s"  # noqa: S608
    query_vars = {"SERVICE_ID": service_id}
    lambda_payload = {"type": "read", "query": query, "query_vars": query_vars}
    response = invoke_dos_db_handler_lambda(lambda_payload)
    data = loads(loads(response))
    return data[0][field_name]


def get_palliative_care(service_id: str) -> bool:
    """Get palliative care from DoS.

    Args:
        service_id (str): Service ID

    Returns:
        bool: True if palliative care is found, False otherwise
    """
    wait_for_service_update(service_id)
    return get_service_sgsd(service_id, 360, 14167)


def get_blood_pressure_sgsd(service_id: str) -> bool:
    """Get blood pressure sgsd from DoS.

    Args:
        service_id (str): Service ID

    Returns:
        bool: True if blood pressure sgsd is found, False otherwise
    """
    wait_for_service_update(service_id)
    return get_service_sgsd(service_id, 360, 14207)


def get_contraception_sgsd(service_id: str) -> bool:
    """Get blood pressure sgsd from DoS.

    Args:
        service_id (str): Service ID

    Returns:
        bool: True if blood pressure sgsd is found, False otherwise
    """
    wait_for_service_update(service_id)
    return get_service_sgsd(service_id, 360, 14210)


def get_service_history(service_id: str) -> list[dict[str, Any]]:
    """Gets the service history from the database.

    Args:
        service_id (str): The service id to get the history for.

    Returns:
        list[dict[str, Any]]: The service history.
    """
    data = []
    retry_counter = 0
    query = "SELECT history FROM servicehistories WHERE serviceid = %(SERVICE_ID)s"
    max_retry = 2
    while not data and retry_counter < max_retry:
        query_vars = {"SERVICE_ID": service_id}
        lambda_payload = {"type": "read", "query": query, "query_vars": query_vars}
        response = invoke_dos_db_handler_lambda(lambda_payload)
        data = loads(loads(response))
        retry_counter += 1
        sleep(30)
    return loads(data[0]["history"]) if data != [] else data


def get_service_history_specified_opening_times(service_id: str) -> dict:
    """This function grabs the latest cmsopentimespecified object for a service id and returns it.

    Args:
        service_id (str): Service id to get service history for

    Returns:
        specified_open_times (dict): Specified opening times from service history
    """
    service_history = get_service_history(service_id)
    return service_history[next(iter(service_history.keys()))]["new"]["cmsopentimespecified"]


def get_service_history_standard_opening_times(service_id: str) -> list:
    """This function grabs the latest standard opening times changes from service history.

    Args:
        service_id (str): Service id to get service history for

    Returns:
        standard_opening_times_from_service_history (list): List of standard opening times from service history
    """
    service_history = get_service_history(service_id)
    return [
        {entry: service_history[next(iter(service_history.keys()))]["new"][entry]}
        for entry in service_history[next(iter(service_history.keys()))]["new"]
        if entry.endswith("day")
    ]


def get_service_sgsd(service_id: str, sgid: int, sdid: int) -> bool:
    """Get service sgsd from DoS.

    Args:
        service_id (str): Service ID
        sgid (int): Service Group ID
        sdid (int): Service Definition ID

    Returns:
        bool: True if service sgsd is found, False otherwise
    """
    query = """SELECT sgsds.id as z_code from servicesgsds sgsds
            WHERE sgsds.serviceid = %(SERVICE_ID)s
            AND sgsds.sgid = %(SG_ID)s
            AND sgsds.sdid  = %(SD_ID)s
            """
    lambda_payload = {
        "type": "read",
        "query": query,
        "query_vars": {"SERVICE_ID": service_id, "SG_ID": sgid, "SD_ID": sdid},
    }
    response = invoke_dos_db_handler_lambda(lambda_payload)
    response = loads(loads(response))
    return len(response) > 0
