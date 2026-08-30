import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def run():
    engine = create_async_engine("postgresql+asyncpg://postgres:postgres@localhost:5432/docuengine")
    async with engine.begin() as conn:
        with open("032_inmutabilidad_fuid.sql", "r", encoding="utf-8") as f:
            sql = f.read()
        await conn.execute(text(sql))
        
        # Grant permissions to docuengine_api
        await conn.execute(text("GRANT ALL PRIVILEGES ON TABLE fuid_transferencias TO docuengine_api"))
        await conn.execute(text("GRANT ALL PRIVILEGES ON TABLE fuid_expedientes_vinculados TO docuengine_api"))

asyncio.run(run())
