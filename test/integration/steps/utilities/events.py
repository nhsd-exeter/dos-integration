from datetime import datetime
from json import dumps, load
from random import choice
from typing import Any, Dict

from .utils import (
    get_change_event_demographics,
    get_change_event_specified_opening_times,
    get_change_event_standard_opening_times,
    get_odscodes_list,
    get_single_service_odscode,
)

odscode_list = None


def create_change_event() -> Dict[str, Any]:
    with open("resources/payloads/expected_schema.json", "r", encoding="utf-8") as json_file:
        payload = load(json_file)
        payload["ODSCode"] = random_odscode()
        print(payload["ODSCode"])
        return payload


def aligned_changed_event() -> Dict[str, Any]:
    with open("resources/payloads/aligned_payload.json", "r", encoding="utf-8") as json_file:
        payload = load(json_file)
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
    global odscode_list
    if odscode_list is None:
        odscode_list = get_odscodes_list()
    return choice(odscode_list)[0]


def get_payload(payload_name: str) -> str:
    values = {"valid": "expected_schema.json", "invalid": "invalid_payload.json"}
    if payload_name in ["valid", "invalid"]:
        payload_file_name = values[payload_name]
    else:
        raise Exception("Unable to find Payload by request name")
    with open(f"./features/resources/payloads/{payload_file_name}", "r", encoding="utf-8") as json_file:
        return dumps(load(json_file))


def build_same_as_dos_change_event():
    # TODO Refactor into change event class
    change_event = create_change_event()
    change_event["ODSCode"] = get_single_service_odscode()
    demographics_data = get_change_event_demographics(change_event["ODSCode"])
    change_event["OrganisationName"] = demographics_data["publicname"]
    change_event["Postcode"] = demographics_data["postcode"]
    change_event["Contacts"][0]["ContactValue"] = demographics_data["web"]
    change_event["Contacts"][1]["ContactValue"] = demographics_data["publicphone"]
    address_keys = ["Address1", "Address2", "Address3", "City", "County"]
    for address_key in address_keys:
        change_event[address_key] = None
    address_parts = demographics_data["address"].split("$")

    if len(address_parts) > 5:
        raise Exception("Address in DoS is too long")

    counter = 0
    for address_part in address_parts:
        change_event[address_keys[counter]] = address_part
        counter += 1

    standard_opening_times = get_change_event_standard_opening_times(demographics_data["id"])
    change_event["OpeningTimes"] = []
    for day in standard_opening_times:
        for opening_times in standard_opening_times[day]:
            change_event["OpeningTimes"].append(
                {
                    "Weekday": day,
                    "Times": f'{opening_times["start_time"]}-{opening_times["end_time"]}',
                    "OpeningTimeType": "General",
                    "AdditionalOpeningDate": "",
                    "IsOpen": True,
                }
            )
    specified_opening_times = get_change_event_specified_opening_times(demographics_data["id"])
    for date in specified_opening_times:
        for opening_times in specified_opening_times[date]:
            str_date = datetime.strptime(date, "%Y-%m-%d")
            change_event["OpeningTimes"].append(
                {
                    "Weekday": "",
                    "Times": f'{opening_times["start_time"]}-{opening_times["end_time"]}',
                    "OpeningTimeType": "Additional",
                    "AdditionalOpeningDate": str_date.strftime("%b %d %Y"),
                    "IsOpen": True,
                }
            )
    print(dumps(change_event, indent=4))
    return change_event
