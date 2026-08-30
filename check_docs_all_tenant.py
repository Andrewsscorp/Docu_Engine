import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def check():
    engine = create_async_engine("postgresql+asyncpg://docuengine_api:api_secure_password_123@localhost:5432/docuengine")
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT id, name FROM sys_tenants"))
        tenants = res.fetchall()
        for t in tenants:
            print("Tenant:", t)
            await conn.execute(text("SELECT set_config('app.current_tenant', :t, false)"), {"t": str(t[0])})
            res2 = await conn.execute(text("SELECT id, agn_expediente_id, file_name, status, paginas_cantidad FROM documents"))
            docs = res2.fetchall()
            for d in docs:
                print(" ", dict(d._mapping))

asyncio.run(check())
