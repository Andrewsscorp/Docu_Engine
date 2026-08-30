import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal
from app.database import get_db_session

async def check():
    async with AsyncSessionLocal() as db:
        # Since RLS is blocking without tenant_id, let's just bypass RLS by running a postgres user?
        # No, wait, if RLS blocks, we can just login with tenant_id!
        # First, let's find the tenant_id of the expediente.
        res = await db.execute(text("SELECT tenant_id FROM agn_expedientes WHERE codigo_expediente = 'AFS-0002-1010-101001-001-007-2026-001'"))
        tenant_id = res.scalar()
        print("Tenant ID:", tenant_id)
        
        # set local
        await db.execute(text("SELECT set_config('app.current_tenant', :t, false)"), {"t": str(tenant_id)})
        
        docs_res = await db.execute(text("SELECT file_name, status, paginas_cantidad FROM documents WHERE agn_expediente_id = (SELECT id FROM agn_expedientes WHERE codigo_expediente = 'AFS-0002-1010-101001-001-007-2026-001')"))
        docs = docs_res.fetchall()
        for d in docs:
            print(dict(d._mapping))

asyncio.run(check())
