import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("SELECT polname, polcmd, polqual FROM pg_policy WHERE polrelid = 'documents'::regclass"))
        policies = res.fetchall()
        for p in policies:
            print(dict(p._mapping))

asyncio.run(check())
