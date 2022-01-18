from json import load, dumps

def load_json_file() -> dict:
    with open(f"./features/resources/payloads/11_expected_schema.json", "r", encoding="utf-8") as json_file:
        return load(json_file)

def get_change_event_string() -> str:
    change_event = load_json_file()
    change_event = dumps(change_event)
    return change_event

def get_change_event_dict() -> dict:
    return load_json_file()

def compile_change_event(change_event: dict) -> dict:
    # Returns:
    #     str: Change event as a dict with string json body
    change_event = dumps(change_event)
    return change_event
