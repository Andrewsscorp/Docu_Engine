import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def test():
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("""
            SELECT t.id, t.nombre_oficial 
            FROM agn_tipologias t
            WHERE t.estado_activo = TRUE 
              AND t.id NOT IN (
                  SELECT tipologia_id FROM agn_subserie_tipologia WHERE estado_regla = TRUE
              )
        """))
        tipologias = [dict(r._mapping) for r in res.fetchall()]
        print(f"Disponibles: {len(tipologias)}")
        for t in tipologias:
            print(t)

asyncio.run(test())
