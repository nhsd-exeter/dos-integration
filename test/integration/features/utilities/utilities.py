import requests
import json
from os import getenv
from features.utilities.get_secrets import get_secret
from json import load, dumps
from boto3 import client
from datetime import datetime

url = "https://"+getenv("URL")
event_processor = getenv("EVENT_PROCESSOR")
lambda_client_functions = client("lambda")

def process_change_event(payload_name: str) -> str:
    headers = {
    'x-api-key': json.loads(get_secret())[getenv('NHS_UK_API_KEY_KEY')],
    'Content-Type': 'application/json'
    }
    payload = get_payload(payload_name)
    global event_request_start_time
    event_request_start_time = datetime.now().timestamp()
    output = requests.request("POST", url, headers=headers, data=payload)
    return output.json()

def get_response(payload: str) -> str:
    payload_name = payload
    response = process_change_event(payload_name)
    return response['Message']

# This matches a payload file with a string describing it from the Steps

def get_payload(payload_name: str) -> str:
    values = {"valid" : "9_valid.json",
            "invalid" : "10_invalid.json",
            "expected": "11_expected_schema.json"
    }
    payload_file_name = values[payload_name]
    with open(f"./features/resources/payloads/{payload_file_name}", "r", encoding="utf-8") as json_file:
        return dumps(load(json_file))

def get_lambda_info(info_param: str) -> str:
    values = {"state" : "State", "status" : "LastUpdateStatus"}
    param = values[info_param]

    response = lambda_client_functions.get_function(
            FunctionName=event_processor
    )
    return response["Configuration"][param]
