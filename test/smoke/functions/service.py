def get_service(ods_code: str) -> None:
    """Get a service from DoS.

    Args:
        ods_code (str): The ODS code of the service to get
    """
    get_service_id_for_ods_code(ods_code)


def get_service_id_for_ods_code(ods_code: str) -> str:
    """Get the service ID for an ODS code.

    Args:
        ods_code (str): The ODS code to get the service ID for

    Returns:
        str: The service ID for the ODS code
    """


def get_demographics_for_service(service_id: str) -> dict:
    """Get the demographics for a service.

    Args:
        service_id (str): The service ID to get the demographics for

    Returns:
        dict: The demographics for the service
    """


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
