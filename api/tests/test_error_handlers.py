import unittest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel
from app.main import app

client = TestClient(app)

# Testar erro de validação (422) com múltiplos campos
class DummyItem(BaseModel):
    name: str
    age: int

@app.post("/dummy-test-route")
def dummy_route(item: DummyItem):
    return item

# Rota temporária para forçar um erro 401 e validar o envelope
@app.get("/dummy-401")
def dummy_401_route():
    raise HTTPException(status_code=401, detail="Não autorizado")


class ErrorHandlersTests(unittest.TestCase):
    def test_404_not_found_returns_standard_error(self):
        response = client.get("/rota-completamente-inventada")
        data = response.json()
        self.assertEqual(response.status_code, 404)
        self.assertIn("code", data)
        self.assertIn("message", data)
        self.assertNotIn("fields", data)

    def test_401_unauthorized_returns_standard_error(self):
        # Testa outro status code (401) para garantir que usa o mesmo envelope
        response = client.get("/dummy-401")
        data = response.json()
        self.assertEqual(response.status_code, 401)
        self.assertIn("code", data)
        self.assertIn("message", data)
        self.assertNotIn("fields", data)

    def test_422_validation_error_with_multiple_fields(self):
        # Envia um JSON vazio quando a rota exige 'name' e 'age'
        response = client.post("/dummy-test-route", json={})
        data = response.json()
        
        self.assertEqual(response.status_code, 422)
        self.assertIn("fields", data)
        # Comprova que o mapeamento funciona para mais de um campo
        self.assertIn("name", data["fields"])
        self.assertIn("age", data["fields"])


if __name__ == "__main__":
    unittest.main()
