from integration.steps.functions.constants import (
    DOS_ADDRESS_FIELD_NAME,
    DOS_ADDRESS_SERVICE_HISTORY_KEY,
    DOS_POSTCODE_FIELD_NAME,
    DOS_POSTCODE_SERVICE_HISTORY_KEY,
    DOS_PUBLIC_PHONE_FIELD_NAME,
    DOS_PUBLIC_PHONE_SERVICE_HISTORY_KEY,
    DOS_STATUS_ID_FIELD_NAME,
    DOS_TOWN_EASTING_NAME,
    DOS_TOWN_FIELD_NAME,
    DOS_TOWN_LATITUDE_NAME,
    DOS_TOWN_LONGITUDE_NAME,
    DOS_TOWN_NORTHING_NAME,
    DOS_WEB_FIELD_NAME,
    DOS_WEB_SERVICE_HISTORY_KEY,
    DOS_ZCODE_SERVICE_HISTORY_KEY,
)


def get_service_table_field_name(plain_english_field_name: str) -> str:
    """Convert a plain English field name to the name of the field in the services table."""
    match plain_english_field_name.lower():
        case "phone_no" | "phone" | "public_phone" | "publicphone":
            field_name = DOS_PUBLIC_PHONE_FIELD_NAME
        case "website" | "web":
            field_name = DOS_WEB_FIELD_NAME
        case "address":
            field_name = DOS_ADDRESS_FIELD_NAME
        case "postcode":
            field_name = DOS_POSTCODE_FIELD_NAME
        case "easting":
            field_name = DOS_TOWN_EASTING_NAME
        case "northing":
            field_name = DOS_TOWN_NORTHING_NAME
        case "town":
            field_name = DOS_TOWN_FIELD_NAME
        case "latitude":
            field_name = DOS_TOWN_LATITUDE_NAME
        case "longitude":
            field_name = DOS_TOWN_LONGITUDE_NAME
        case "status":
            field_name = DOS_STATUS_ID_FIELD_NAME
        case _:
            msg = f"Error!.. Input parameter '{plain_english_field_name}' not compatible"
            raise ValueError(msg)
    return field_name


def get_service_history_data_key(plain_english_field_name: str) -> str:
    """Convert a plain English field name to the name of the field in the services table."""
    match plain_english_field_name.lower():
        case "phone_no" | "phone" | "public_phone" | "publicphone":
            field_name = DOS_PUBLIC_PHONE_SERVICE_HISTORY_KEY
        case "website" | "web":
            field_name = DOS_WEB_SERVICE_HISTORY_KEY
        case "address":
            field_name = DOS_ADDRESS_SERVICE_HISTORY_KEY
        case "postcode":
            field_name = DOS_POSTCODE_SERVICE_HISTORY_KEY
        case "zcode" | "z-code" | "z code":
            field_name = DOS_ZCODE_SERVICE_HISTORY_KEY
        case _:
            msg = f"Error!.. Input parameter '{plain_english_field_name}' not compatible"
            raise ValueError(msg)
    return field_name
