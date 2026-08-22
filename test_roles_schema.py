import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test():
    engine = create_async_engine('postgresql+asyncpg://docuengine_api:api_password@localhost/docuengine_db')
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'roles'"))
        for r in res.all():
            print(r.column_name)

asyncio.run(test())
