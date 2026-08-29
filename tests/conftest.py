import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
import sys
import os
from unittest.mock import AsyncMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from app.main import app
except ImportError:
    from fastapi import FastAPI
    app = FastAPI()

try:
    from database import get_db_session
except ImportError:
    try:
        from app.database import get_db_session
    except ImportError:
        async def get_db_session():
            yield None

@pytest.fixture
def mock_db_session():
    mock_session = AsyncMock()
    return mock_session

@pytest.fixture
def override_get_db(mock_db_session):
    async def _override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db_session] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def async_client(override_get_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
