import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        query = text("""
            SELECT id
            FROM documents
            WHERE status = 'PENDING'
            ORDER BY created_at ASC
            FOR UPDATE SKIP LOCKED
            LIMIT 1
        """)
        res = await db.execute(query)
        print("Worker Query Result:", res.fetchone())

asyncio.run(main())
