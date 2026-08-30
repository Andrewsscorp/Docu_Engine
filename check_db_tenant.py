import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def check():
    async with AsyncSessionLocal() as db:
        # Simulate set_config for the tenant that owns this expediente
        res_t = await db.execute(text("SELECT tenant_id FROM agn_expedientes WHERE codigo_expediente = 'AFS-0002-1010-101001-001-007-2026-001'"))
        tenant = res_t.scalar()
        await db.execute(text("SELECT set_config('app.current_tenant', :t, false)"), {"t": str(tenant)})
        
        res = await db.execute(text("SELECT id, status, paginas_cantidad, file_name FROM documents WHERE agn_expediente_id = (SELECT id FROM agn_expedientes WHERE codigo_expediente = 'AFS-0002-1010-101001-001-007-2026-001')"))
        docs = res.fetchall()
        print("Docs WITH RLS:", [dict(d._mapping) for d in docs])

asyncio.run(check())
