import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os

async def run():
    engine = create_async_engine("postgresql+asyncpg://docuengine_api:api_secure_password_123@localhost:5432/docuengine")
    with open("migrations/005_append_only_audit.sql", "r", encoding="utf-8") as f:
        sql_content = f.read()
    
    async with engine.begin() as conn:
        await conn.execute(text(sql_content))
    print("Migration 005 applied successfully!")
            
asyncio.run(run())
