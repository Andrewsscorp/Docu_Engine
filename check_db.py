import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def check():
    async with AsyncSessionLocal() as db:
        # Check closed expedientes
        res = await db.execute(text("SELECT id, codigo_expediente, nombre_expediente, estado FROM agn_expedientes WHERE estado = 'CERRADO'"))
        expedientes = res.fetchall()
        print("Cerrados:", [dict(r._mapping) for r in expedientes])
        
        for exp in expedientes:
            res_docs = await db.execute(text("SELECT id, status, paginas_cantidad FROM documents WHERE agn_expediente_id = :eid"), {"eid": exp.id})
            docs = res_docs.fetchall()
            print(f"Docs for {exp.codigo_expediente}:", [dict(d._mapping) for d in docs])

asyncio.run(check())
