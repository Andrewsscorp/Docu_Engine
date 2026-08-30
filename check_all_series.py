import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        res = await db.execute(text("SELECT id, codigo, nombre FROM agn_series"))
        for r in res.fetchall():
            print(dict(r._mapping))
            
        res = await db.execute(text("SELECT id, codigo, nombre FROM agn_subseries"))
        for r in res.fetchall():
            print(dict(r._mapping))

asyncio.run(main())
