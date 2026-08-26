from functools import lru_cache

from app.application.services.health_service import HealthService
from app.infrastructure.repositories.in_memory_health_repository import (
    InMemoryHealthRepository,
)


@lru_cache
def get_health_service() -> HealthService:
    repository = InMemoryHealthRepository()
    return HealthService(repository=repository)
