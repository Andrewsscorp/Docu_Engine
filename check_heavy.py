import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        res = await db.execute(text("SELECT file_name, paginas_cantidad, file_size_bytes FROM documents WHERE id = 'c3afcaf1-9e6d-46d4-a331-75217844f768'"))
        r = res.fetchone()
        print(f"Name: {r.file_name}, Pages: {r.paginas_cantidad}, Size: {r.file_size_bytes}")

asyncio.run(main())
