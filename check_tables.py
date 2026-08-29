import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os

DATABASE_URL = 'postgresql+asyncpg://postgres:superadmin_password@localhost:5432/docuengine'
engine = create_async_engine(DATABASE_URL)

async def check():
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        print(res.fetchall())

asyncio.run(check())
