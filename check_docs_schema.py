import asyncio
from sqlalchemy import text
from app.database import engine

async def get_schema():
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'documents';"))
        cols = res.fetchall()
        for col in cols:
            print(f"{col[0]}: {col[1]}")

asyncio.run(get_schema())
