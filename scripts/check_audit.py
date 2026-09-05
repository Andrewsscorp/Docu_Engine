import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def run():
    engine = create_async_engine("postgresql+asyncpg://docuengine_api:api_secure_password_123@localhost:5432/docuengine")
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        for row in res:
            if "audit" in row[0] or "log" in row[0] or "trazabilidad" in row[0]:
                print(row[0])
            
asyncio.run(run())
