from fastapi.testclient import TestClient
from app.main import app
import json
import asyncio
from app.security import session_signer

client = TestClient(app)

# Create a valid session token for SuperAdmin
session_data = {
    "user_id": "11111111-1111-1111-1111-111111111111",
    "tenant_id": "22222222-2222-2222-2222-222222222222",
    "role_id": "33333333-3333-3333-3333-333333333333" # Assuming this is SuperAdmin
}
cookie = session_signer.dumps(session_data)

client.cookies.set("sessionId", cookie)

response = client.post(
    "/api/v1/agn/tipologias/diccionario",
    json={
        "nombre_oficial": "TEST TIPOLOGIA HTTPX",
        "soporte_origen": "ELECTRONICO_NATIVO",
        "formatos_permitidos": ["PDF/A"],
        "clasificacion": "PUBLICA",
        "exige_firma": False
    }
)

print("Status:", response.status_code)
print("Response:", response.text)
