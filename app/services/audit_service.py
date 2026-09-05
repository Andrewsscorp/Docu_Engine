from app.database import AsyncSessionLocal
from sqlalchemy import text
import json

async def log_audit_sgdea_async(expediente_id: str, usuario_id: str, tipo_evento: str, ip_origen: str, payload_legal: dict):
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text('''
                INSERT INTO log_auditoria_sgdea (id_expediente, id_usuario, tipo_evento, ip_origen, payload_legal)
                VALUES (:eid, :uid, :tev, :ip, CAST(:payload AS JSONB))
            '''), {
                "eid": expediente_id,
                "uid": usuario_id,
                "tev": tipo_evento,
                "ip": ip_origen,
                "payload": json.dumps(payload_legal)
            })
            await session.commit()
    except Exception as e:
        print(f"Error asíncrono en log_audit_sgdea_async: {e}")