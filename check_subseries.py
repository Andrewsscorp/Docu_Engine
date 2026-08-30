import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        res = await db.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'agn_subseries'"))
        for row in res.fetchall():
            print(f"{row.column_name}: {row.data_type}")

asyncio.run(main())
