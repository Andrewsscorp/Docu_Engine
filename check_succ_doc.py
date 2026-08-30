import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        res = await db.execute(text("SELECT id, file_path FROM documents WHERE id = '2682c593-92a9-4ed9-a53e-92348c35b0c1'"))
        print(res.fetchone())

asyncio.run(main())
