import os
import httpx
from typing import Dict, Any

NOVU_API_KEY = os.getenv("NOVU_API_KEY", "docuengine_dummy_key_in_dev")
NOVU_API_URL = os.getenv("NOVU_API_URL", "http://localhost:3000/v1")

class NotificadorEventos:
    def __init__(self):
        self.headers = {
            "Authorization": f"ApiKey {NOVU_API_KEY}",
            "Content-Type": "application/json"
        }
    
    async def sync_subscriber(self, user_id: str, email: str, first_name: str, last_name: str = ""):
        """Registra a un usuario en Novu como suscriptor."""
        async with httpx.AsyncClient() as client:
            payload = {
                "subscriberId": str(user_id),
                "email": email,
                "firstName": first_name,
                "lastName": last_name
            }
            try:
                response = await client.post(
                    f"{NOVU_API_URL}/subscribers", 
                    headers=self.headers,
                    json=payload,
                    timeout=5.0
                )
                return response.status_code in [201, 200]
            except Exception as e:
                print(f"[NOVU] Error sincronizando suscriptor: {e}")
                return False

    async def trigger_event(self, event_name: str, user_id: str, payload: Dict[str, Any]):
        """Dispara un evento/workflow en Novu para un suscriptor."""
        async with httpx.AsyncClient() as client:
            data = {
                "name": event_name,
                "to": {
                    "subscriberId": str(user_id)
                },
                "payload": payload
            }
            try:
                response = await client.post(
                    f"{NOVU_API_URL}/events/trigger",
                    headers=self.headers,
                    json=data,
                    timeout=5.0
                )
                return response.status_code == 201
            except Exception as e:
                print(f"[NOVU] Error disparando evento {event_name}: {e}")
                return False

    async def get_recent_notifications(self, user_id: str, page: int = 0, limit: int = 10):
        """Obtiene las notificaciones recientes de un suscriptor."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{NOVU_API_URL}/subscribers/{user_id}/notifications",
                    headers=self.headers,
                    params={"page": page, "limit": limit},
                    timeout=5.0
                )
                if response.status_code == 200:
                    return response.json()
                return {"data": []}
            except Exception as e:
                print(f"[NOVU] Error obteniendo notificaciones: {e}")
                return {"data": []}
                
    async def get_unread_count(self, user_id: str):
        """Obtiene el conteo de notificaciones no leídas."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{NOVU_API_URL}/subscribers/{user_id}/notifications/unseen",
                    headers=self.headers,
                    timeout=5.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", {}).get("count", 0)
                return 0
            except Exception as e:
                print(f"[NOVU] Error obteniendo conteo unread: {e}")
                return 0

novu_client = NotificadorEventos()
