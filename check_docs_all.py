import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("SELECT * FROM documents LIMIT 5"))
        docs = res.fetchall()
        for d in docs:
            print(dict(d._mapping))

asyncio.run(check())
