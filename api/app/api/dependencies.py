from functools import lru_cache
from fastapi import HTTPException, Request, status
from app.infrastructure.auth.jwt import decode_access_token
from app.infrastructure.config.settings import get_settings
import jwt

from app.application.services.health_service import HealthService
from app.infrastructure.repositories.in_memory_health_repository import (
    InMemoryHealthRepository,
)


@lru_cache
def get_health_service() -> HealthService:
    repository = InMemoryHealthRepository()
    return HealthService(repository=repository)

def current_user(request: Request) -> int:
    settings = get_settings()
    token = request.cookies.get(settings.jwt_cookie_name)

    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        user_id = decode_access_token(token)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user_id

