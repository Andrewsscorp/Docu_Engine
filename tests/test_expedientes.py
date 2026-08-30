import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_get_expedientes_module():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/agn/expedientes/module")
        assert response.status_code in (200, 401, 307)
        
        response = await ac.get("/api/v1/agn/expedientes/module", headers={"hx-target": "expedientes-results-grid"})
        assert response.status_code in (200, 401, 307)
