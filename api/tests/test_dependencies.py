import unittest

from fastapi import HTTPException

from app.api.dependencies import current_user
from app.infrastructure.auth.jwt import create_access_token
from app.infrastructure.config.settings import get_settings


class FakeRequest:
    def __init__(self, cookies: dict[str, str]) -> None:
        self.cookies = cookies


class CurrentUserTests(unittest.TestCase):
    def test_sem_cookie_responde_401(self) -> None:
        request = FakeRequest(cookies={})

        with self.assertRaises(HTTPException) as contexto:
            current_user(request)

        self.assertEqual(contexto.exception.status_code, 401)

    def test_token_valido_resolve_a_conta(self) -> None:
        settings = get_settings()
        token = create_access_token(1)
        request = FakeRequest(cookies={settings.jwt_cookie_name: token})

        resultado = current_user(request)

        self.assertEqual(resultado, 1)

    def test_token_invalido_responde_401(self) -> None:
        settings = get_settings()
        request = FakeRequest(cookies={settings.jwt_cookie_name: "token-quebrado"})

        with self.assertRaises(HTTPException) as contexto:
            current_user(request)

        self.assertEqual(contexto.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()