import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def test():
    async with AsyncSessionLocal() as db:
        await db.execute(text("SELECT set_config('app.tenant_id', '22222222-2222-2222-2222-222222222222', false)"))
        res = await db.execute(text("SELECT * FROM agn_indice_electronico ORDER BY fecha_accion ASC"))
        events = [dict(r._mapping) for r in res.fetchall()]
        for e in events:
            print(f"{e['accion']} at {e['fecha_accion']}")

asyncio.run(test())
