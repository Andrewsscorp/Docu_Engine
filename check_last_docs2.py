import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        res = await db.execute(text("SELECT id, file_name, status, file_path FROM documents WHERE id IN ('0f00adc1-b624-451b-8a52-31f617733e41', '93318f97-809d-43a6-800a-c135a88eae64')"))
        rows = res.fetchall()
        for r in rows:
            print(f"ID: {r.id}, Name: {r.file_name}, Status: {r.status}, Path: {r.file_path}")

asyncio.run(main())
