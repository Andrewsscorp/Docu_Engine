import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def apply_migration():
    async with AsyncSessionLocal() as session:
        # Drop if exists
        await session.execute(text("DROP MATERIALIZED VIEW IF EXISTS vista_fuid_detalle_subserie"))
        with open("031_vista_fuid.sql", "r", encoding="utf-8") as f:
            sql = f.read()
        await session.execute(text(sql))
        await session.commit()
        print("Materialized view created!")

asyncio.run(apply_migration())
