import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def main():
    engine = create_async_engine("postgresql+asyncpg://postgres:postgres@localhost:5432/docuengine")
    async with engine.begin() as conn:
        res = await conn.execute(text("""
            SELECT t.id, t.codigo_tipologia, t.nombre 
            FROM agn_tipologias t
            WHERE t.estado_activo = TRUE 
              AND t.tenant_id = '22222222-2222-2222-2222-222222222222'
              AND t.id NOT IN (
                  SELECT tipologia_id FROM agn_subserie_tipologia WHERE subserie_id = '75db37c0-c195-4dcc-8826-5013353327e9' AND estado_regla = TRUE
              )
        """))
        print(res.fetchall())
        
asyncio.run(main())
