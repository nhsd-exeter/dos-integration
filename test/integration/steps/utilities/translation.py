from .constants import (
    DOS_ADDRESS_FIELD_NAME,
    DOS_POSTCODE_FIELD_NAME,
    DOS_PUBLIC_PHONE_FIELD_NAME,
    DOS_WEB_FIELD_NAME,
    DOS_PUBLIC_PHONE_SERVICE_HISTORY_KEY,
    DOS_WEB_SERVICE_HISTORY_KEY,
    DOS_ADDRESS_SERVICE_HISTORY_KEY,
    DOS_POSTCODE_SERVICE_HISTORY_KEY,
)


def get_service_table_field_name(plain_english_field_name: str) -> str:
    """Convert a plain English field name to the name of the field in the services table"""
    match plain_english_field_name.lower():
        case "phone_no":
            field_name = DOS_PUBLIC_PHONE_FIELD_NAME
        case "website":
            field_name = DOS_WEB_FIELD_NAME
        case "address":
            field_name = DOS_ADDRESS_FIELD_NAME
        case "postcode":
            field_name = DOS_POSTCODE_FIELD_NAME
        case _:
            raise ValueError(f"Error!.. Input parameter '{plain_english_field_name}' not compatible")
    return field_name


def get_service_history_data_key(plain_english_field_name: str) -> str:
    """Convert a plain English field name to the name of the field in the services table"""
    match plain_english_field_name.lower():
        case "phone_no":
            field_name = DOS_PUBLIC_PHONE_SERVICE_HISTORY_KEY
        case "website":
            field_name = DOS_WEB_SERVICE_HISTORY_KEY
        case "address":
            field_name = DOS_ADDRESS_SERVICE_HISTORY_KEY
        case "postcode":
            field_name = DOS_POSTCODE_SERVICE_HISTORY_KEY
        case _:
            raise ValueError(f"Error!.. Input parameter '{plain_english_field_name}' not compatible")
    return field_name
