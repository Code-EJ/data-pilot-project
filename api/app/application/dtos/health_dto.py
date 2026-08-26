from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HealthCheckDTO:
    is_healthy: bool
