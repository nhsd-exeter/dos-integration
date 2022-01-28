from json import load, dumps
import csv
import itertools
import random
from typing import Dict, Any


def load_payload_file() -> dict:
    with open("./features/resources/payloads/expected_schema.json", "r", encoding="utf-8") as json_file:
        payload = (load(json_file))
        payload["ODSCode"] = random_odscode()
        return payload


def get_change_request() -> Dict[str, Any]:
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
    with open("./features/resources/valid_ods_codes.csv") as csv_file:
        csv_data = csv.reader(csv_file, delimiter=",")
        ods_list = list(itertools.chain(*list(csv_data)))
        valid_odscode = random.choices(ods_list, k=1)
        return valid_odscode[0]


def get_change_event() -> dict:
    return load_payload_file()


def get_payload(payload_name: str) -> str:
    values = {"valid": "expected_schema.json", "invalid": "invalid_payload.json"}
    if payload_name in ["valid", "invalid"]:
        payload_file_name = values[payload_name]
    else:
        raise Exception("Unable to find Payload by request name")
    with open(f"./features/resources/payloads/{payload_file_name}", "r", encoding="utf-8") as json_file:
        return dumps(load(json_file))
