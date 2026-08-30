import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()

async def run():
    # Use the app's standard database URL which connects successfully
    import sys
    sys.path.append(".")
    from app.database import DATABASE_URL
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        with open("032_inmutabilidad_fuid.sql", "r", encoding="utf-8") as f:
            sql = f.read().lstrip("\ufeff")
        await conn.execute(text(sql))

asyncio.run(run())
