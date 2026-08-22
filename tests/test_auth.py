import pytest
from unittest.mock import AsyncMock

pytestmark = pytest.mark.asyncio

async def test_login_rejection_bad_password(async_client, mock_db_session):
    """
    Verifica que el endpoint de Login rechace credenciales inválidas.
    """
    mock_result = AsyncMock()
    mock_row = AsyncMock()
    mock_row._mapping = {"id": "123", "password_hash": "hash_real", "mfa_secret": None, "role_name": "admin"}
    mock_row.__getitem__.side_effect = mock_row._mapping.__getitem__
    mock_result.fetchone.return_value = mock_row
    mock_db_session.execute.return_value = mock_result

    response = await async_client.post(
        "/api/login", 
        json={"username": "admin", "password": "wrongpassword"}
    )
    
    assert response.status_code == 200
    assert "Credenciales inválidas" in response.text
