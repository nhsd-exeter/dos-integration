from json import dumps, load


def load_json_file(filename: str) -> str:
    """Load Json file from resource folder

    Args:
        filename (str): Name of the file to be loaded

    Returns:
        str: File as string
    """
    with open(f"features/resources/{filename}", "r", encoding="utf-8") as json_file:
        return load(json_file)


def get_change_request_name(variable: str):
    """Works out which resource file to load

    Args:
        variable (str): How to determine which resource file to load

    Raises:
        Exception: If variable passed in isn't within list

    Returns:
        [type]: File name
    """
    if variable in ["Success", "valid"]:
        change_request_file_name = "valid_change_request.json"
    elif variable in ["Failure", "invalid"]:
        change_request_file_name = "invalid_change_request.json"
    else:
        raise Exception("Unable to set change request name")
    return change_request_file_name


def read_log_file() -> str:
    """Reads the log file

    Returns:
        str: The log file as a string
    """
    file_path = "../../build/automation/tmp/log_file.txt"
    with open(file_path, "r", encoding="utf-8") as file:
        log_file = file.read()
        return log_file


def setup_change_event() -> dict:
    """Sets up valid change event

    Returns:
        str: Change event as a dict with json string body
    """
    change_event = load_json_file("valid_change_event.json")
    change_event["body"] = dumps(change_event["body"])
    return change_event


def load_change_event() -> str:
    """Loads change event, ready for modification

    Returns:
        str: Change event as a string
    """
    change_event = load_json_file("valid_change_event.json")
    return change_event


def compile_change_event(change_event: dict) -> dict:
    """Compiles change event body to json

    Args:
        change_event (dict): Change event as a dictionary

    Returns:
        str: Change event as a dict with string json body
    """
    change_event["body"] = dumps(change_event["body"])
    return change_event
