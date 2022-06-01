from datetime import datetime
from json import dumps, load
from random import choice
from typing import Any, Dict

from dateutil.relativedelta import relativedelta

from .utils import (
    get_odscodes_list,
)
from .change_event import build_same_as_dos_change_event

pharmacy_odscode_list = None
dentist_odscode_list = None


def create_change_event(service_type: str) -> Dict[str, Any]:
    with open("resources/payloads/expected_schema.json", "r", encoding="utf-8") as json_file:
        payload = load(json_file)
        match service_type.upper():
            case "PHARMACY":
                payload["ODSCode"] = random_pharmacy_odscode()
            case "DENTIST":
                payload["ODSCode"] = random_dentist_odscode()
            case _:
                raise ValueError(f"Service type {service_type} does not exist")
        payload["OrganisationName"] = f'{payload["OrganisationName"]} {datetime.now()}'
        print(payload["ODSCode"])
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


def set_opening_times_change_event(service_type: str):
    change_event = build_same_as_dos_change_event(service_type)
    date = datetime.today() + relativedelta(months=1)
    has_set_closed_day = False
    for day in change_event["OpeningTimes"]:
        if day["IsOpen"] and day["OpeningTimeType"] == "General":
            closed_day = day["Weekday"]
            has_set_closed_day = True
            break
    if has_set_closed_day is False:
        raise ValueError("ERROR!.. Unable to find 'Open' Standard opening time")
    change_event["OpeningTimes"] = list(filter(lambda day: day["Weekday"] != closed_day, change_event["OpeningTimes"]))
    change_event["OpeningTimes"].append(
        {
            "Weekday": closed_day,
            "OpeningTime": "",
            "ClosingTime": "",
            "Times": "-",
            "OffsetOpeningTime": 0,
            "OffsetClosingTime": 0,
            "OpeningTimeType": "General",
            "AdditionalOpeningDate": "",
            "IsOpen": False,
        }
    )
    change_event["OpeningTimes"].append(
        {
            "Weekday": "",
            "OpeningTime": "",
            "ClosingTime": "",
            "Times": "-",
            "OffsetOpeningTime": 0,
            "OffsetClosingTime": 0,
            "OpeningTimeType": "Additional",
            "AdditionalOpeningDate": date.strftime("%b %d %Y"),
            "IsOpen": False,
        }
    )
    return change_event
