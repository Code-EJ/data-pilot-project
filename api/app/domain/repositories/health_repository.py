from abc import ABC, abstractmethod

from app.domain.entities.health import Health


class HealthRepository(ABC):
    @abstractmethod
    def check(self) -> Health:
        """Retorna o estado da infraestrutura consultada."""
