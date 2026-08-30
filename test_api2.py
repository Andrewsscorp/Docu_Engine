from fastapi.testclient import TestClient
from app.main import app
import asyncio
from app.database import AsyncSessionLocal
from sqlalchemy import text
from app.security import session_signer

async def test():
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("SELECT id FROM roles WHERE name = 'SuperAdmin'"))
        role_id = str(res.scalar())
        
        from app.rbac import load_rbac_cache
        await load_rbac_cache(db)

    client = TestClient(app)
    session_data = {
        "user_id": "11111111-1111-1111-1111-111111111111",
        "tenant_id": "22222222-2222-2222-2222-222222222222",
        "role_id": role_id
    }
    cookie = session_signer.dumps(session_data)
    client.cookies.set("sessionId", cookie)
    
    response = client.post(
        "/api/v1/agn/tipologias/diccionario",
        json={
            "nombre_oficial": "TEST TIPOLOGIA HTTPX 2",
            "soporte_origen": "ELECTRONICO_NATIVO",
            "formatos_permitidos": ["PDF/A"],
            "clasificacion": "PUBLICA",
            "exige_firma": False
        }
    )
    print("Status:", response.status_code)
    print("Response:", response.text)

asyncio.run(test())
