import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def test():
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("SELECT tipologia_id, estado_regla FROM agn_subserie_tipologia"))
        rules = [dict(r._mapping) for r in res.fetchall()]
        print(f"Rules: {len(rules)}")
        for r in rules:
            print(r)

asyncio.run(test())
