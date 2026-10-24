import unittest
from datetime import datetime, timedelta, timezone
import jwt
from app.infrastructure.auth.jwt import create_access_token, decode_access_token
from app.infrastructure.config.settings import get_settings

class JwtTests(unittest.TestCase):
    def test_token_valido(self) -> None:
        token = create_access_token(1)

        resultado = decode_access_token(token)

        self.assertEqual(resultado, 1)

    def test_token_expirado_e_rejeitado(self) -> None:
        settings = get_settings()
        payload = {
            "sub": "1",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
        }
        token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

        with self.assertRaises(jwt.ExpiredSignatureError):
            decode_access_token(token)

    def test_assinatura_invalida_e_rejeitada(self) -> None:
        settings = get_settings()
        payload = {
            "sub": "1",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }
        token = jwt.encode(payload, "uma-chave-diferente-da-configurada", algorithm=settings.jwt_algorithm)

        with self.assertRaises(jwt.InvalidTokenError):
            decode_access_token(token)
            
    def test_payload_nao_contem_papel_nem_organizacao(self) -> None:
        settings = get_settings()
        token = create_access_token(1)

        payload = jwt.decode(token, key=settings.jwt_secret, algorithms=[settings.jwt_algorithm])

        self.assertEqual(set(payload.keys()), {"sub", "exp"})