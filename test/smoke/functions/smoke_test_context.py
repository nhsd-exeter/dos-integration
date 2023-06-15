from dataclasses import dataclass, field


@dataclass(init=True)
class SmokeTestContext:
    """Context for smoke tests."""

    original_service: dict = field(default_factory=dict)
