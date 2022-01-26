import json
from json import load, dumps
import csv
import itertools
import random


def load_payload_file() -> dict:
    with open("./features/resources/payloads/expected_schema.json", "r", encoding="utf-8") as json_file:
        return load(json_file)

def random_odscode()-> str:
    with open('./features/resources/valid_ods_codes.csv') as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        ods_list= list(itertools.chain(*list(csv_data)))
        valid_odscode=random.choices(ods_list, k=1)
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
