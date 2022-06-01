from json import dumps, load
from random import choice
from typing import Any, Dict

from .utils import (
    get_odscodes_list,
)

pharmacy_odscode_list = None
dentist_odscode_list = None

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
                "address": {
                    "address_lines": ["85 Peachfield Road", "CHAPEL ROW", "South Godshire"],
                    "post_code": "RG7 1DB",
                },
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


def random_pharmacy_odscode() -> str:
    global pharmacy_odscode_list
    if pharmacy_odscode_list is None:
        lambda_payload = {"type": "get_pharmacy_odscodes"}
        pharmacy_odscode_list = get_odscodes_list(lambda_payload)
    return choice(pharmacy_odscode_list)[0]


def random_dentist_odscode() -> str:
    global dentist_odscode_list
    if dentist_odscode_list is None:
        lambda_payload = {"type": "get_dentist_odscodes"}
        dentist_odscode_list = get_odscodes_list(lambda_payload)
    odscode = choice(dentist_odscode_list)[0]
    return f"{odscode[0]}0{odscode[1:]}"


def get_payload(payload_name: str) -> str:
    values = {"valid": "expected_schema.json", "invalid": "invalid_payload.json"}
    if payload_name in ["valid", "invalid"]:
        payload_file_name = values[payload_name]
    else:
        raise Exception("Unable to find Payload by request name")
    with open(f"./features/resources/payloads/{payload_file_name}", "r", encoding="utf-8") as json_file:
        return dumps(load(json_file))
