import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def test():
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("SELECT count(*) FROM documents"))
        print(f"Count: {res.scalar()}")

asyncio.run(test())
