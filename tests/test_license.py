import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient

from app.security import session_signer

pytestmark = pytest.mark.asyncio

def generate_admin_cookie():
    return session_signer.dumps({
        "tenant_id": "22222222-2222-2222-2222-222222222222",
        "user_id": "f85c1b50-b4ed-4454-aa44-418c78e04eb2",
        "role_id": "11ef9c5d-1cd7-4849-81d7-fb9004a3dc5e"
    })

@pytest.fixture
def admin_cookies():
    return {"sessionId": generate_admin_cookie()}

async def test_license_ui_unauthenticated(async_client: AsyncClient):
    response = await async_client.get("/api/v1/license/ui")
    assert response.status_code == 401

async def test_license_ui_authenticated_admin(async_client: AsyncClient, mock_db_session, admin_cookies):
    mock_result = AsyncMock()
    mock_row = ['{"exp_timestamp": 2000000000, "max_activations": 100}']
    mock_result.fetchone.return_value = mock_row
    
    mock_count_result = AsyncMock()
    mock_count_result.fetchone.return_value = [5]
    
    mock_db_session.execute.side_effect = [mock_result, mock_count_result]

    with patch('app.security.check_permission', return_value=True):
        response = await async_client.get("/api/v1/license/ui", cookies=admin_cookies)
        assert response.status_code == 200
        assert "Tiempo Restante" in response.text
        assert "Usuarios de la Licencia" in response.text

async def test_license_renew_invalid_signature(async_client: AsyncClient, admin_cookies):
    malformed_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.dummy_payload.invalid_signature"
    
    with patch('app.security.check_permission', return_value=True):
        with patch('fastapi_csrf_protect.CsrfProtect.validate_csrf', return_value=None):
            response = await async_client.post(
                "/api/v1/license/renew",
                data={
                    "hwid_hash": "dummy_hwid",
                    "license_token": malformed_token,
                    "csrf_token": "valid"
                },
                cookies=admin_cookies
            )
            assert response.status_code == 200
            res_json = response.json()
            assert res_json["status"] == "error"
            assert "malformado" in res_json["detail"] or "Spoofing" in res_json["detail"]