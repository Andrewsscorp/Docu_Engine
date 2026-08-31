import pytest
from httpx import AsyncClient
from uuid import uuid4

# =========================================================================
# FASE 2: LABORATORIO DE SEGURIDAD OFENSIVA (DAST) Y AISLAMIENTO
# =========================================================================

pytestmark = pytest.mark.asyncio

async def test_sec_ten_001_consulta_cruzada(mock_client_tenant_a, mock_db_tenant_b_doc_id):
    """
    SEC-TEN-001: Usuario de Tenant A consulta documento de Tenant B.
    Esperado: El sistema debe bloquear la lectura devolviendo 404 (No 403, para no confirmar existencia).
    """
    response = await mock_client_tenant_a.get(f"/api/v1/documents/{mock_db_tenant_b_doc_id}")
    assert response.status_code == 404, "Vulnerabilidad P0: Fuga de datos cruzada permitida"

async def test_sec_ten_002_descarga_cruzada(mock_client_tenant_a, mock_db_tenant_b_doc_id):
    """
    SEC-TEN-002: Descarga de archivo físico de otro tenant.
    Esperado: Bloqueo de descarga 404.
    """
    response = await mock_client_tenant_a.get(f"/api/v1/documents/{mock_db_tenant_b_doc_id}/download")
    assert response.status_code == 404, "Vulnerabilidad P0: Robo de binarios cruzado permitido"

async def test_sec_file_001_path_traversal(mock_client_tenant_a):
    """
    SEC-FILE-001: Intento de Path Traversal en el nombre del archivo.
    Esperado: Rechazo del upload o sanitización estricta.
    """
    malicious_filename = "../../../etc/passwd.pdf"
    file_payload = {"file": (malicious_filename, b"%PDF-1.4 mock", "application/pdf")}
    response = await mock_client_tenant_a.post("/api/v1/documents/upload", files=file_payload)
    
    # Debe ser rechazado (400) o sanitizado devolviendo un nombre limpio.
    if response.status_code == 200:
        data = response.json()
        assert "../" not in data.get("file_name", ""), "Vulnerabilidad P0: Path Traversal detectado en BD"
    else:
        assert response.status_code in [400, 422, 403]

async def test_sec_file_002_mime_falsificado(mock_client_tenant_a):
    """
    SEC-FILE-002: Subida de archivo ejecutable con MIME de PDF falso.
    Esperado: El backend debe detectar la firma binaria real y rechazarlo (400/415).
    """
    # Contenido de un script bash, pero engañando al Content-Type
    malicious_payload = b"#!/bin/bash\nrm -rf /"
    file_payload = {"file": ("documento.pdf", malicious_payload, "application/pdf")}
    
    response = await mock_client_tenant_a.post("/api/v1/documents/upload", files=file_payload)
    
    # DocuEngine utiliza filetype/magic-numbers para detectar esto. Debe rechazarlo.
    assert response.status_code in [400, 415, 422], "Vulnerabilidad P0: Motor MIME engañado por metadata falsa"
