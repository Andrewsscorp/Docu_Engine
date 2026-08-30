import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        print("--- ÚLTIMOS EXPEDIENTES ---")
        res = await db.execute(text("SELECT id, nombre_expediente, subserie_id, created_at FROM agn_expedientes ORDER BY created_at DESC LIMIT 3"))
        for r in res.fetchall():
            print(dict(r._mapping))
            
        print("--- ÚLTIMAS SUBSERIES ---")
        res = await db.execute(text("SELECT id, nombre, serie_id, total_expedientes, created_at FROM agn_subseries ORDER BY created_at DESC LIMIT 3"))
        for r in res.fetchall():
            print(dict(r._mapping))

asyncio.run(main())
