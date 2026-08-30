import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def test():
    async with AsyncSessionLocal() as db:
        await db.execute(text("DELETE FROM agn_indice_electronico WHERE accion = 'CERRAR_EXPEDIENTE' OR accion = 'CIERRE_EXPEDIENTE'"))
        await db.commit()

asyncio.run(test())
