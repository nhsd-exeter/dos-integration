from json import load


def load_json_file(filename: str) -> str:
    with open(f"features/resources/{filename}", "r", encoding="utf-8") as json_file:
        return load(json_file)


def get_change_request_name(variable: str):
    if variable in ["Success", "valid"]:
        change_request_file_name = "valid_change_request.json"
    elif variable in ["Failure", "invalid"]:
        change_request_file_name = "invalid_change_request.json"
    else:
        raise Exception("Unable to set change request name")
    return change_request_file_name
