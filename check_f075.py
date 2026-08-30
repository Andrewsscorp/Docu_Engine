import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        res = await db.execute(text("SELECT id, file_path FROM documents WHERE id = 'f075740a-97f8-4340-b66d-21025ed07d25'"))
        print(res.fetchone())

asyncio.run(main())
