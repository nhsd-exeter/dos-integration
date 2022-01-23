from json import load, dumps


def load_payload_file() -> dict:
    with open(f"./features/resources/payloads/11_expected_schema.json", "r", encoding="utf-8") as json_file:
        return load(json_file)

def get_change_event() -> str:
    change_event = load_payload_file()
    return change_event

def get_change_event_dict() -> dict:
    return load_payload_file()

def compile_change_event(change_event: dict) -> dict:
    change_event = dumps(change_event)
    return change_event
