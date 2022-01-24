from json import load, dumps


def load_payload_file() -> dict:
    with open("./features/resources/payloads/expected_schema.json", "r", encoding="utf-8") as json_file:
        return load(json_file)


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
