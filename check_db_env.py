import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import os
from dotenv import load_dotenv

load_dotenv()

async def check():
    engine = create_async_engine(os.getenv("DATABASE_URL"))
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT id FROM agn_expedientes WHERE codigo_expediente = 'AFS-0002-1010-101001-001-007-2026-001'"))
        exp_id = res.scalar()
        if not exp_id:
            print("Expediente not found")
            return
            
        res_docs = await conn.execute(text("SELECT id, status, paginas_cantidad, file_name FROM documents WHERE agn_expediente_id = :eid"), {"eid": exp_id})
        docs = res_docs.fetchall()
        print("Docs with NO RLS config:", [dict(d._mapping) for d in docs])

asyncio.run(check())
