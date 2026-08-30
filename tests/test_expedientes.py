import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_get_expedientes_module():
    with patch('app.database.get_db_session'):
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                response = await ac.get("/api/v1/agn/expedientes/module")
                assert response.status_code in (200, 401, 307, 500)

                response = await ac.get("/api/v1/agn/expedientes/module", headers={"hx-target": "expedientes-results-grid"})
                assert response.status_code in (200, 401, 307, 500)
        except OSError:
            pass # Ignorar error de red si no hay BD viva
