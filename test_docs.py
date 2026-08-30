import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def test():
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("SELECT id, file_name, status, tipologia_id, agn_expediente_id FROM documents ORDER BY created_at DESC LIMIT 5"))
        docs = [dict(r._mapping) for r in res.fetchall()]
        print(f"Total docs: {len(docs)}")
        for d in docs:
            print(d)

asyncio.run(test())
