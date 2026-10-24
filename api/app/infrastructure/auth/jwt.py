from datetime import datetime, timedelta, timezone

import jwt

from app.infrastructure.config.settings import get_settings

def create_access_token(user_id: int) -> str:
    settings = get_settings()
    now_utc = datetime.now(timezone.utc)
    expiration = now_utc + timedelta(seconds=settings.jwt_expiration_seconds)
    payload = {"sub": str(user_id), "exp": expiration}
    token = jwt.encode(payload, settings.jwt_secret, settings.jwt_algorithm)

    return token

def decode_access_token(token: str) -> int:
    settings = get_settings()
    payload = jwt.decode(token, key=settings.jwt_secret, algorithms=[settings.jwt_algorithm])

    return int(payload["sub"])
