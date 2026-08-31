import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import Request, HTTPException
from app.routers.agn import vincular_documento_expediente

@pytest.mark.asyncio
async def test_inmutabilidad_expediente_cerrado():
    mock_db = AsyncMock()
    mock_request = MagicMock(spec=Request)
    fake_session = {"tenant_id": "tenant_123", "user_id": "user_123", "permissions": ["documentos:crear"]}
    
    mock_res = MagicMock()
    mock_res.fetchone.return_value = ['CERRADO']
    mock_db.execute.return_value = mock_res
    
    with pytest.raises(HTTPException) as excinfo:
        await vincular_documento_expediente("exp_123", "doc_456", "tipo_789", fake_session, mock_db)
    
    assert excinfo.value.status_code == 403
    assert "CERRADO" in excinfo.value.detail or "Inmutabilidad" in excinfo.value.detail
