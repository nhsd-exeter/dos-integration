from time import time


def total_time(start_time) -> float:
    return int((time() - start_time) * 1000)
