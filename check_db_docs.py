import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("SELECT id, codigo_expediente, nombre_expediente, estado FROM agn_expedientes WHERE estado = 'CERRADO'"))
        expedientes = res.fetchall()
        for exp in expedientes:
            res_docs = await db.execute(text("SELECT id, status, paginas_cantidad, file_name FROM documents WHERE agn_expediente_id = :eid"), {"eid": exp.id})
            docs = res_docs.fetchall()
            print(f"Docs for {exp.codigo_expediente} ({exp.nombre_expediente}):", [dict(d._mapping) for d in docs])

asyncio.run(check())
