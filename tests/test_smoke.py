import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_smoke_app_boot():
    """Smoke test to verify the app boots up and responds to a basic GET"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/login", follow_redirects=True)
        assert response.status_code == 200
