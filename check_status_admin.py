import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def check():
    async with AsyncSessionLocal() as db:
        # We know we need tenant_id and is_superadmin to bypass
        await db.execute(text("SELECT set_config('app.current_tenant', '22222222-2222-2222-2222-222222222222', false)"))
        await db.execute(text("SELECT set_config('app.is_superadmin', 'true', false)"))
        
        docs_res = await db.execute(text("SELECT file_name, status, paginas_cantidad FROM documents WHERE agn_expediente_id = (SELECT id FROM agn_expedientes WHERE codigo_expediente = 'AFS-0002-1010-101001-001-007-2026-001')"))
        docs = docs_res.fetchall()
        for d in docs:
            print(dict(d._mapping))

asyncio.run(check())
