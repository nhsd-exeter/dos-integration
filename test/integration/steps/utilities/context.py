from dataclasses import dataclass

from requests import Response

from .change_event import ChangeEvent


@dataclass(init=True)
class Context:
    change_event: ChangeEvent | None = None
    service_id: str | None = None
    correlation_id: str | None = None
    response: Response | None = None
    sequence_number: int | None = None
    start_time: str | None = None
    other: dict | None = None
    # Other used as a catch all for any other data that is not covered by the above and only used in a couple tests

    def __repr__(self) -> str:
        return (
            f"Context(correlation_id={self.correlation_id}, sequence_number={self.sequence_number}"
            f", change_event={self.change_event}, service_id={self.service_id})"
        )
