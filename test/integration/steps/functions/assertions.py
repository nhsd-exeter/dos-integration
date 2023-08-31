def assert_standard_closing(dos_times: list, ce_times: list[dict]) -> int:
    """Function to assert standard closing times changes.

    Args:
        dos_times (list): The times pulled from DOS
        ce_times (list): The times pulled from the change event to compare too

    Returns:
        int: If more than 0 assertions are made then the test passes.
    """
    counter = 0
    for entry in ce_times:
        if entry["times"] == "closed":
            currentday = entry["name"]
            for dates in dos_times:
                if currentday == next(iter(dates.keys())):
                    assert dates[currentday]["changetype"] == "delete", "Open when expected closed"
                    assert (
                        "add" not in dates[currentday]["data"]
                    ), "ERROR: Unexpected add field found in service history"
                    counter += 1
    return counter


def assert_standard_openings(
    change_type: str,
    dos_times: list[dict],
    ce_times: list[dict],
    strict: bool | None = None,
) -> int:
    """Function to assert standard opening times changes. Added to remove complexity for sonar.

    Args:
        change_type (Str): The type of change being asserted
        dos_times (list[Dict]): The times pulled from DOS
        ce_times (Dict): The times pulled from the change event to compare too
        strict (bool | None): If true, will assert that the changetype is the same as the one passed in

    Returns:
        counter (Int): The amount of assertions made
    """
    counter = 0
    valid_change_types = ["add", "modify"]
    for entry in dos_times:
        currentday = next(iter(entry.keys()))
        for dates in ce_times:
            if dates["name"] == currentday:
                assert entry[currentday]["data"]["add"][0] == dates["times"], "ERROR: Dates do not match"
                if strict:
                    assert entry[currentday]["changetype"] == change_type, "ERROR: Incorrect changetype"
                else:
                    assert entry[currentday]["changetype"] in valid_change_types, "ERROR: Incorrect changetype"
                if entry[currentday]["changetype"] == "add":
                    assert "remove" not in entry[currentday]["data"], "ERROR: Remove is present in service history"
                elif entry[currentday]["changetype"] == "modify":
                    assert "remove" in entry[currentday]["data"], f"ERROR: Remove is not present for {currentday}"
                counter += 1
    return counter
