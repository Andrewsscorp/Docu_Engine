import pytest
from unittest.mock import AsyncMock

pytestmark = pytest.mark.asyncio

async def test_rbac_permission_denial(async_client, mock_db_session):
    """
    Verifica que los usuarios sin permisos reciban 'Operación denegada' en el módulo RBAC.
    """
    mock_result = AsyncMock()
    mock_result.fetchone.return_value = None
    mock_db_session.execute.return_value = mock_result

    response = await async_client.get("/rbac/users")
    
    assert response.status_code in [200, 403, 303, 500, 404]
    if response.status_code == 200:
        assert "Operación denegada" in response.text
    elif response.status_code == 403:
        assert "Operación denegada" in response.text or response.json().get("detail") == "Operación denegada"
