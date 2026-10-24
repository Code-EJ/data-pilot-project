from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from starlette.exceptions import HTTPException

from app.api.dependencies import current_user
from app.infrastructure.auth.jwt import create_access_token, decode_access_token
from app.infrastructure.config.settings import get_settings
from app.main import http_exception_handler


@pytest.fixture
def protected_client():
    app = FastAPI(exception_handlers={HTTPException: http_exception_handler})

    @app.get("/protected")
    def protected(user_id: int = Depends(current_user)):
        return {"user_id": user_id}

    with TestClient(app) as client:
        yield client


@pytest.mark.parametrize(
    "claim,value",
    [
        pytest.param("sub", None, id="sub-null"),
        pytest.param("sub", "", id="sub-empty"),
        pytest.param("sub", "abc", id="sub-nonnumeric"),
        pytest.param("sub", "0", id="sub-zero"),
        pytest.param("sub", "-1", id="sub-negative"),
        pytest.param("sub", "1.5", id="sub-fraction"),
        pytest.param("sub", " 1", id="sub-whitespace"),
        pytest.param("sub", "١", id="sub-nonascii"),
        pytest.param("sub", 1, id="sub-number"),
        pytest.param("sub", True, id="sub-boolean"),
        pytest.param("sub", [], id="sub-list"),
        pytest.param("sub", {}, id="sub-object"),
        pytest.param("exp", None, id="exp-null"),
        pytest.param("exp", "invalid", id="exp-nonnumeric"),
        pytest.param("exp", "9999999999", id="exp-string"),
        pytest.param("exp", True, id="exp-boolean"),
        pytest.param("exp", [], id="exp-list"),
        pytest.param("exp", {}, id="exp-object"),
        pytest.param("exp", float("inf"), id="exp-infinity"),
        pytest.param("exp", float("nan"), id="exp-nan"),
        pytest.param("exp", 0, id="exp-expired"),
        pytest.param("nbf", [], id="nbf-invalid-type"),
        pytest.param("iat", {}, id="iat-invalid-type"),
    ],
)
def test_invalid_claims_return_generic_401(protected_client, claim, value):
    payload = {
        "sub": "1",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        claim: value,
    }
    assert_invalid_token(protected_client, payload)


@pytest.mark.parametrize("claim", ["sub", "exp"])
def test_required_claims_return_generic_401(protected_client, claim):
    payload = {
        "sub": "1",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    del payload[claim]
    assert_invalid_token(protected_client, payload)


def assert_invalid_token(client, payload):
    settings = get_settings()
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)

    client.cookies.set(settings.jwt_cookie_name, token)
    response = client.get("/protected")

    assert response.status_code == 401
    assert response.json() == {"code": "unauthorized", "message": "Unauthorized"}


@pytest.mark.parametrize("token", [None, "token-quebrado", ""])
def test_missing_or_malformed_cookie_returns_401(protected_client, token):
    if token is not None:
        protected_client.cookies.set(get_settings().jwt_cookie_name, token)
    response = protected_client.get("/protected")
    assert response.status_code == 401
    assert response.json() == {"code": "unauthorized", "message": "Unauthorized"}


def test_valid_token_authenticates_protected_route(protected_client):
    protected_client.cookies.set(get_settings().jwt_cookie_name, create_access_token(42))
    response = protected_client.get("/protected")
    assert response.status_code == 200
    assert response.json() == {"user_id": 42}
