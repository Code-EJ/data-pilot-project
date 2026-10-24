from datetime import datetime, timedelta, timezone
from math import isfinite

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
    try:
        payload = jwt.decode(
            token,
            key=settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp"]},
        )
    except (TypeError, ValueError, OverflowError) as exc:
        # Algumas claims com tipos inválidos falham na conversão feita pelo PyJWT.
        raise jwt.InvalidTokenError("Invalid token claims") from exc

    expiration = payload["exp"]
    if type(expiration) not in (int, float) or (
        isinstance(expiration, float) and not isfinite(expiration)
    ):
        raise jwt.InvalidTokenError("Invalid expiration")

    subject = payload["sub"]
    if not isinstance(subject, str) or not subject.isascii() or not subject.isdecimal():
        raise jwt.InvalidTokenError("Invalid user id")

    try:
        user_id = int(subject)
    except ValueError as exc:
        raise jwt.InvalidTokenError("Invalid user id") from exc
    if user_id <= 0:
        raise jwt.InvalidTokenError("Invalid user id")

    return user_id
