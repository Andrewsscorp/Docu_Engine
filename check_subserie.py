import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("""
            SELECT e.codigo_expediente, e.nombre_expediente, 
                   s.nombre as subserie_nombre, se.nombre as serie_nombre
            FROM agn_expedientes e
            LEFT JOIN agn_subseries s ON e.subserie_id = s.id
            LEFT JOIN agn_series se ON s.serie_id = se.id
            WHERE e.codigo_expediente = 'AFS-0002-1010-101001-001-007-2026-001'
        """))
        row = res.fetchone()
        print(dict(row._mapping) if row else "Not found")

asyncio.run(check())
