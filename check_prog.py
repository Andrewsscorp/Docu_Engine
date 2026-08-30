import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        res = await db.execute(text("SELECT id, status, ocr_progress_percent FROM documents WHERE id = 'c3afcaf1-9e6d-46d4-a331-75217844f768'"))
        r = res.fetchone()
        print(f"ID: {r.id}, Status: {r.status}, Prog: {r.ocr_progress_percent}")

asyncio.run(main())
