import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        res = await db.execute(text("SELECT id, status, ocr_progress_percent FROM documents WHERE id = 'da7b5932-f349-4509-8364-d13c950c0c8e'"))
        r = res.fetchone()
        print(f"ID: {r.id}, Status: {r.status}, Prog: {r.ocr_progress_percent}")

asyncio.run(main())
