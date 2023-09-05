from time import time_ns

from locust import FastHttpUser

from .ods_codes import ODS_CODES


def send_change_event(request_name: str, request: FastHttpUser, valid_ods_code: bool) -> FastHttpUser:
    """Send a valid change event. Set playload before calling this function.

    Args:
        request_name (str): The name of the request
        request (FastHttpUser): The request class
        valid_ods_code (bool): Whether to use a valid ods code or not


    Returns:
        FastHttpUser: The change event class
    """
    request.payload["ODSCode"] = ODS_CODES.get_valid_ods_code() if valid_ods_code else ODS_CODES.get_invalid_ods_code()
    request.payload["OrganisationName"] = f'{request.payload["Address1"]} {time_ns()}'
    request.headers = setup_headers()
    request.headers["x-api-key"] = request.api_key
    request.client.post(
        "",
        headers=request.headers,
        json=request.payload,
        name=request_name,
    )
    return request


def setup_headers() -> dict[str, str]:
    """Setup the headers for the change event endpoint."""
    return {"sequence-number": str(time_ns())}
