from dataclasses import dataclass


@dataclass(init=True)
class Context:
    correlation_id: str | None = None
    change_event: dict | None = None
