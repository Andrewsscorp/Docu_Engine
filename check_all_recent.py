import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        print("--- LAST 5 SERIES ---")
        res = await db.execute(text("SELECT id, codigo, nombre, seccion_id, subseccion_id, created_at FROM agn_series ORDER BY created_at DESC LIMIT 5"))
        for r in res.fetchall():
            print(dict(r._mapping))
            
        print("--- LAST 5 SUBSERIES ---")
        res = await db.execute(text("SELECT id, codigo, nombre, serie_id, created_at FROM agn_subseries ORDER BY created_at DESC LIMIT 5"))
        for r in res.fetchall():
            print(dict(r._mapping))

asyncio.run(main())
