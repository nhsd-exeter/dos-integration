from dataclasses import dataclass, field


@dataclass(init=True, repr=True)
class SmokeTestContext:
    """Context for smoke tests."""

    original_service: dict = field(default_factory=dict)
