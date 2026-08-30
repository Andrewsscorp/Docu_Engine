import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def test():
    async with AsyncSessionLocal() as db:
        await db.execute(text("SELECT set_config('app.tenant_id', '22222222-2222-2222-2222-222222222222', false)"))
        res = await db.execute(text("SELECT file_name FROM documents"))
        docs = [dict(r._mapping) for r in res.fetchall()]
        print(f"Total: {len(docs)}")
        for d in docs:
            print(d['file_name'])

asyncio.run(test())
