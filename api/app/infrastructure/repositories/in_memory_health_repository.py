from app.domain.entities.health import Health
from app.domain.repositories.health_repository import HealthRepository


class InMemoryHealthRepository(HealthRepository):
    """Adaptador temporário até a infraestrutura de banco existir."""

    def check(self) -> Health:
        return Health(is_healthy=True)
