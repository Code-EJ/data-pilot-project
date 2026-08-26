from app.application.dtos.health_dto import HealthCheckDTO
from app.domain.repositories.health_repository import HealthRepository


class HealthService:
    def __init__(self, repository: HealthRepository) -> None:
        self._repository = repository

    def check(self) -> HealthCheckDTO:
        health = self._repository.check()
        return HealthCheckDTO(is_healthy=health.is_healthy)
