import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        res = await db.execute(text("SELECT is_nullable FROM information_schema.columns WHERE table_name = 'documents' AND column_name = 'tipologia_id';"))
        print(res.fetchone())

asyncio.run(main())
