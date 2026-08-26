import unittest

from app.application.services.health_service import HealthService
from app.domain.entities.health import Health
from app.domain.repositories.health_repository import HealthRepository


class UnhealthyRepository(HealthRepository):
    def check(self) -> Health:
        return Health(is_healthy=False)


class HealthServiceTests(unittest.TestCase):
    def test_maps_domain_entity_to_dto(self) -> None:
        result = HealthService(UnhealthyRepository()).check()

        self.assertFalse(result.is_healthy)


if __name__ == "__main__":
    unittest.main()
