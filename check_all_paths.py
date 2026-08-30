import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        res = await db.execute(text("SELECT id, file_path, status FROM documents WHERE status = 'FAILED' OR file_path LIKE '%/%' OR file_path LIKE '%\\%'"))
        rows = res.fetchall()
        for r in rows:
            print(r)

asyncio.run(main())
