import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        res = await db.execute(text("SELECT id, status, ocr_progress_percent FROM documents WHERE status IN ('PENDING', 'EXTRACTING', 'FAILED') ORDER BY created_at ASC"))
        rows = res.fetchall()
        for r in rows:
            print(f"ID: {r.id}, Status: {r.status}, Prog: {r.ocr_progress_percent}")

asyncio.run(main())
