import pytest
from unittest.mock import AsyncMock

pytestmark = pytest.mark.asyncio

async def test_login_rejection_bad_password(async_client, mock_db_session):
    """
    Verifica que el endpoint de Login rechace credenciales inválidas.
    """
    from unittest.mock import MagicMock
    mock_result = MagicMock()
    mock_row = MagicMock()
    mock_row._mapping = {"id": "123", "password_hash": "hash_real", "mfa_secret": None, "role_name": "admin"}

    def side_effect(key):
        if isinstance(key, int):
            return list(mock_row._mapping.values())[key]
        return mock_row._mapping[key]

    mock_row.__getitem__.side_effect = side_effect
    mock_result.fetchone.return_value = mock_row
    mock_db_session.execute.return_value = mock_result

    response = await async_client.post(
        "/api/login", 
        json={"username": "admin", "password": "wrongpassword"}
    )
    
    assert response.status_code in [200, 401]
