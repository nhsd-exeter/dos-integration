from json import load, dumps


def load_payload_file() -> dict:
    with open("./features/resources/payloads/11_expected_schema.json", "r", encoding="utf-8") as json_file:
        return load(json_file)


def get_change_event() -> dict:
    return load_payload_file()


""" This matches a payload file with a string describing it from the Steps """


def get_payload(payload_name: str) -> str:
    values = {"valid": "11_expected_schema.json", "invalid": "10_invalid.json"}
    if payload_name in ["valid", "invalid"]:
        payload_file_name = values[payload_name]
    else:
        raise Exception("Unable to find Payload by request name")
    with open(f"./features/resources/payloads/{payload_file_name}", "r", encoding="utf-8") as json_file:
        return dumps(load(json_file))
