import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        res = await db.execute(text("SELECT id, nombre_expediente, serie_id, subserie_id FROM agn_expedientes ORDER BY created_at DESC LIMIT 3"))
        for r in res.fetchall():
            print(dict(r._mapping))

asyncio.run(main())
