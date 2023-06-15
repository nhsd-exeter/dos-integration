from .aws import invoke_dos_db_handler_lambda
from json import loads


def get_service(ods_code: str) -> None:
    """Get a service from DoS.

    Args:
        ods_code (str): The ODS code of the service to get
    """
    service_id = get_service_id_for_ods_code(ods_code)
    demographics = get_demographics_for_service(service_id)


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


def get_demographics_for_service(service_id: str) -> dict:
    """Get the demographics for a service.

    Args:
        service_id (str): The service ID to get the demographics for

    Returns:
        dict: The demographics for the service
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


def get_specified_opening_times_for_service(service_id: str) -> dict:
    """Get the specified opening times for a service.

    Args:
        service_id (str): The service ID to get the specified opening times for

    Returns:
        dict: The specified opening times for the service
    """


def get_service_history(service_id: str) -> dict:
    """Get the service history for a service.

    Args:
        service_id (str): The service ID to get the service history for

    Returns:
        dict: The service history for the service
    """
