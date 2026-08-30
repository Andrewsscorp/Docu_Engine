import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def test():
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("SELECT id, nombre_oficial, tenant_id FROM agn_tipologias ORDER BY created_at DESC"))
        tipologias = [dict(r._mapping) for r in res.fetchall()]
        print(f"Total: {len(tipologias)}")
        for t in tipologias:
            print(t)

asyncio.run(test())
