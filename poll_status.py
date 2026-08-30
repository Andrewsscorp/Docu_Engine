import asyncio
from app.database import get_global_db_session
from sqlalchemy import text
import time

async def main():
    for _ in range(5):
        async for db in get_global_db_session():
            res = await db.execute(text("SELECT id, status, ocr_progress_percent FROM documents WHERE id IN ('0f00adc1-b624-451b-8a52-31f617733e41', '93318f97-809d-43a6-800a-c135a88eae64')"))
            rows = res.fetchall()
            for r in rows:
                print(f"ID: {r.id}, Status: {r.status}, Prog: {r.ocr_progress_percent}")
            print("---")
        time.sleep(2)

asyncio.run(main())
