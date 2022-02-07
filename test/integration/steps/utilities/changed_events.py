from json import dumps, load
from random import choice
from typing import Any, Dict

from .utils import search_dos_db

VALID_SERVICE_TYPES = [13, 131, 132, 134, 137]
VALID_STATUS_ID = 1


def changed_event() -> Dict[str, Any]:
    with open("resources/payloads/expected_schema.json", "r", encoding="utf-8") as json_file:
        payload = load(json_file)
        payload["ODSCode"] = random_odscode()
        return payload


def change_request() -> Dict[str, Any]:
    return {
        "change_payload": {
            "reference": "EDFA07-16",
            "system": "DoS Integration",
            "message": "DoS Integration CR. correlation-id: EDFA07-16",
            "service_id": "37652",
            "changes": {
                "website": None,
                "phone": None,
                "public_name": "My Test Pharmacy 21",
                "address": ["85 Peachfield Road", "CHAPEL ROW", "South Godshire"],
                "postcode": "RG7 1DB",
                "opening_days": {
                    "Monday": [],
                    "Tuesday": [],
                    "Wednesday": [],
                    "Thursday": [],
                    "Friday": [],
                    "Saturday": [],
                    "Sunday": [],
                },
            },
        },
        "correlation_id": "c1",
        "message_received": 1643306908893,
        "dynamo_record_id": "d8842511670361f8db0f52d5ab86e78c",
        "ods_code": "FA007",
    }


def random_odscode() -> str:
    query = (
        f"SELECT LEFT(odscode, 5) FROM services WHERE typeid IN {tuple(VALID_SERVICE_TYPES)} "
        f"AND statusid = '{VALID_STATUS_ID}'"
    )
    odscode_list = search_dos_db(query)
    return choice(odscode_list)[0]


def get_payload(payload_name: str) -> str:
    values = {"valid": "expected_schema.json", "invalid": "invalid_payload.json"}
    if payload_name in ["valid", "invalid"]:
        payload_file_name = values[payload_name]
    else:
        raise Exception("Unable to find Payload by request name")
    with open(f"./features/resources/payloads/{payload_file_name}", "r", encoding="utf-8") as json_file:
        return dumps(load(json_file))
