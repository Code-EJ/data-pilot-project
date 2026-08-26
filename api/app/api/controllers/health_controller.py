from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.api.dependencies import get_health_service
from app.application.services.health_service import HealthService

router = APIRouter(tags=["health"])


@router.get("/health", status_code=status.HTTP_204_NO_CONTENT)
async def healthcheck(
    service: Annotated[HealthService, Depends(get_health_service)],
) -> Response:
    service.check()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
