from json import load


def load_json_file(filename: str) -> str:
    with open(f"features/resources/{filename}", "r", encoding="utf-8") as json_file:
        return load(json_file)
