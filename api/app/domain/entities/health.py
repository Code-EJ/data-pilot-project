from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Health:
    is_healthy: bool
