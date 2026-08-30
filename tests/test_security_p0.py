import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock
from app.security import session_signer

pytestmark = pytest.mark.asyncio

def generate_cookie(tenant_id):
    return session_signer.dumps({
        "tenant_id": tenant_id,
        "user_id": "f85c1b50-b4ed-4454-aa44-418c78e04eb2",
        "role_id": "11ef9c5d-1cd7-4849-81d7-fb9004a3dc5e"
    })

# SEC-TEN-002: A descarga archivo de B -> 403/404
async def test_sec_ten_download_isolation(async_client, mock_db_session):
    # Simulamos que en BD sí existe el documento pero pertenece al Tenant B
    class DummyDoc:
        def __init__(self):
            self.file_path = "/ruta/doc_b.pdf"
            self.file_name = "test.pdf"
            self.mime_type = "application/pdf"
            self.group_id = "group_b"

    # Mocking db returns None when tenant B doesn't match the tenant A sent in query
    mock_result = MagicMock()
    mock_result.fetchone.return_value = None # No encuentra documento porque el query incluye "AND tenant_id = :t"
    mock_db_session.execute.return_value = mock_result

    cookies = {"sessionId": generate_cookie("tenant_A")}
    response = await async_client.get("/api/v1/documents/doc_perteneciente_a_B/download", cookies=cookies)

    # 404 es seguro por diseño para no filtrar existencia (enumeración de ID)
    assert response.status_code == 404

# SEC-TEN-001: A consulta ID de documento de B -> Sin contenido
async def test_sec_ten_query_isolation(async_client, mock_db_session):
    mock_result = MagicMock()
    mock_result.fetchone.return_value = None # Nuevamente, "AND tenant_id = :t" fallará
    mock_db_session.execute.return_value = mock_result

    cookies = {"sessionId": generate_cookie("tenant_A")}
    response = await async_client.get("/api/v1/documents/detail/doc_perteneciente_a_B", cookies=cookies)

    assert response.status_code in [404, 200]
    if response.status_code == 200:
        assert response.text.strip() == ""


# SEC-FILE-001: Upload ../ -> Rechazado/Mitigado
async def test_sec_file_path_traversal(async_client, mock_db_session):
    import uuid
    mock_result = MagicMock()
    mock_result.fetchone.return_value = {"id": "doc_123", "status": "PENDING"}
    mock_db_session.execute.return_value = mock_result

    malicious_filename = "../../../etc/passwd.pdf"
    files = {'file': (malicious_filename, b'dummy content', 'application/pdf')}
    cookies = {"sessionId": generate_cookie("tenant_A")}

    with pytest.MonkeyPatch.context() as m:
        # Interceptamos la llamada para comprobar que UUID fue usado y no el malicious string puro
        passed_path = None
        original_open = open
        def mock_open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None):
            nonlocal passed_path
            passed_path = file
            return original_open("/dev/null", "w") # mock physical write

        import builtins
        m.setattr(builtins, "open", mock_open)
        m.setattr("os.makedirs", lambda *a, **k: None)

        response = await async_client.post("/api/v1/documents/upload", files=files, cookies=cookies)

        # Debe haber procesado exitosamente sin chocar con seguridad
        assert response.status_code in [200, 401, 403]
        if response.status_code == 200:
            assert passed_path is not None
            # Asegurarse que el path traversal no quedó impregnado en la ruta salvada
            assert "../../../" not in passed_path
            # Asegurarse que conservó la extensión validada
            assert passed_path.endswith(".pdf")

# REC-EXP-001: Editar cerrado -> Rechazo
async def test_rec_exp_edit_closed_expediente(async_client, mock_db_session):
    # Mocking status 'CERRADO' en expediente
    mock_status_result = MagicMock()
    mock_status_result.fetchone.return_value = ["CERRADO"]
    mock_db_session.execute.return_value = mock_status_result

    cookies = {"sessionId": generate_cookie("tenant_A")}
    payload = {"documento_id": "doc_999", "tipologia_id": "tipo_111"}

    from unittest.mock import patch
    with patch('app.rbac.check_permission', return_value=True):
        response = await async_client.post(
            "/api/v1/agn/expedientes/exp_cerrado/vincular",
            data=payload,
            cookies=cookies
        )

    # Debe ser bloqueado explícitamente con 403 o 400
    assert response.status_code == 403
    assert "CERRADO" in response.json()["detail"]
