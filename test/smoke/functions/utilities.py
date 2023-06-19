from datetime import time


def seconds_since_midnight(time: time) -> int:
    """Returns the number of seconds since midnight for the given time."""
    return time.hour * 60 * 60 + time.minute * 60 + time.second
