import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal
import json

async def test():
    async with AsyncSessionLocal() as db:
        try:
            res = await db.execute(text("""
                INSERT INTO agn_tipologias (
                    nombre_oficial, soporte_origen, formatos_permitidos, 
                    clasificacion, exige_firma, tenant_id, usuario_creador, estado_activo
                )
                VALUES (:nom, :sop, CAST(:form AS JSONB), :clas, :firma, :t, :uid, TRUE)
                RETURNING id
            """), {
                "nom": "TEST NUEVA TIPOLOGIA",
                "sop": "Físico Digitalizado",
                "form": json.dumps(["PDF/A", "XML"]),
                "clas": "PUBLICA",
                "firma": False,
                "t": "22222222-2222-2222-2222-222222222222",
                "uid": "11111111-1111-1111-1111-111111111111"
            })
            print("Success ID:", res.scalar())
            await db.commit()
        except Exception as e:
            print("ERROR:", e)

asyncio.run(test())
