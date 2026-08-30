import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        res = await db.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'agn_series' AND column_name = 'total_expedientes'"))
        for r in res.fetchall():
            print(dict(r._mapping))

asyncio.run(main())
