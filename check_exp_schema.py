import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'agn_expedientes'"))
        cols = res.fetchall()
        for c in cols:
            print(f"{c[0]}: {c[1]}")

asyncio.run(check())
