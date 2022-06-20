from dataclasses import dataclass


# TODO: Use this class to store the context of the test.
@dataclass(init=True)
class Context:
    correlation_id: str | None = None
    change_event: dict | None = None
