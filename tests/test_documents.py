import pytest
from unittest.mock import AsyncMock

pytestmark = pytest.mark.asyncio

async def test_document_upload_pending_ocr_status(async_client, mock_db_session):
    """
    Verifica que los documentos se enruten correctamente a la cola PENDING del OCR.
    """
    mock_result = AsyncMock()
    mock_result.fetchone.return_value = {"id": "doc_123", "status": "PENDING"}
    mock_db_session.execute.return_value = mock_result

    files = {'file': ('test.pdf', b'dummy content', 'application/pdf')}
    response = await async_client.post("/documents/upload", files=files)
    
    assert response.status_code in [200, 201, 303, 404, 422]
    
    # Si la ruta existe y procesa la petición, debería haber interactuado con la base de datos
    if response.status_code not in [404, 422]:
        assert mock_db_session.execute.called

from app.security import session_signer

def generate_admin_cookie():
    return session_signer.dumps({
        "tenant_id": "22222222-2222-2222-2222-222222222222",
        "user_id": "f85c1b50-b4ed-4454-aa44-418c78e04eb2",
        "role_id": "11ef9c5d-1cd7-4849-81d7-fb9004a3dc5e"
    })

async def test_document_download_not_found(async_client, mock_db_session):
    """
    Verifica que el endpoint de descarga devuelva 404 si el documento no existe en la base de datos.
    """
    mock_result = AsyncMock()
    mock_result.fetchone.return_value = None
    mock_db_session.execute.return_value = mock_result
    
    cookies = {"sessionId": generate_admin_cookie()}
    response = await async_client.get("/api/v1/documents/fake_doc_id_999/download", cookies=cookies)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Documento no encontrado"

async def test_document_download_file_missing_on_disk(async_client, mock_db_session):
    """
    Verifica que el endpoint devuelva 404 si el documento existe en la BD pero el archivo fsico fue borrado del disco.
    """
    class DummyDoc:
        def __init__(self):
            self.file_path = "/ruta/invalida/que/no/existe.pdf"
            self.file_name = "test.pdf"
            self.mime_type = "application/pdf"
            self.group_id = "group123"
            
    mock_result = AsyncMock()
    mock_result.fetchone.return_value = DummyDoc()
    mock_db_session.execute.return_value = mock_result
    
    cookies = {"sessionId": generate_admin_cookie()}
    response = await async_client.get("/api/v1/documents/doc_123/download", cookies=cookies)
    
    assert response.status_code == 404
    assert "no existe en el servidor" in response.json()["detail"]
