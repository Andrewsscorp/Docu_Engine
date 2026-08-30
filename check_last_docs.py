import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        res = await db.execute(text("SELECT id, file_name, status, ocr_confidence_score FROM documents ORDER BY created_at DESC LIMIT 5"))
        rows = res.fetchall()
        for r in rows:
            print(f"ID: {r.id}, Name: {r.file_name}, Status: {r.status}, Score: {r.ocr_confidence_score}")

asyncio.run(main())
