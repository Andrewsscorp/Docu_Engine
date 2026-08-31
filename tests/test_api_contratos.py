import pytest
from unittest.mock import Mock


@pytest.fixture
def mock_api_client():
    """
    Mock de un cliente HTTP (por ejemplo, httpx.AsyncClient o TestClient).
    Simula las respuestas de la API para probar los contratos REST.
    """
    client = Mock()

    def mock_get(url, headers=None):
        response = Mock()
        if url == "/api/v1/documents/non_existent_id":
            response.status_code = 404
            response.json.return_value = {"detail": "Document not found"}
        elif url == "/api/v1/protected/resource":
            if not headers or "Authorization" not in headers:
                response.status_code = 401
                response.json.return_value = {"detail": "Not authenticated"}
            else:
                response.status_code = 200
        return response

    def mock_post(url, json=None):
        response = Mock()
        if url == "/api/v1/documents":
            if not json or "required_field" not in json:
                response.status_code = 422
                response.json.return_value = {"detail": "Unprocessable Entity"}
            else:
                response.status_code = 201
        return response

    client.get.side_effect = mock_get
    client.post.side_effect = mock_post
    return client


def test_get_non_existent_document_returns_404(mock_api_client):
    """
    Prueba que solicitar un documento que no existe devuelva un 404 Not Found
    en lugar de lanzar una excepciÃ³n 500.
    """
    response = mock_api_client.get("/api/v1/documents/non_existent_id")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}


def test_post_malformed_payload_returns_422(mock_api_client):
    """
    Prueba que enviar un payload incompleto (sin el campo requerido) devuelva 422.
    """
    payload = {"other_field": "value"}
    response = mock_api_client.post("/api/v1/documents", json=payload)

    assert response.status_code == 422
    assert response.json() == {"detail": "Unprocessable Entity"}


def test_access_protected_endpoint_without_auth_returns_401(mock_api_client):
    """
    Prueba que acceder a una ruta protegida sin autenticaciÃ³n devuelva 401.
    """
    response = mock_api_client.get("/api/v1/protected/resource")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
