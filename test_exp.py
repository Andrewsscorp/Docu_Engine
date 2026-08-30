import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def test():
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("SELECT id, codigo_expediente, estado FROM agn_expedientes"))
        rows = [dict(r._mapping) for r in res.fetchall()]
        for r in rows:
            print(f"{r['codigo_expediente']}: {r['estado']}")

asyncio.run(test())
