import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        res = await db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'agn_%';"))
        tables = [r[0] for r in res.fetchall()]
        print("Tables:", tables)

asyncio.run(main())
