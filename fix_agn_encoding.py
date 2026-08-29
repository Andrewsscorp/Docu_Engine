import asyncio
from sqlalchemy import text
from app.database import get_db_session_context

async def fix_encoding():
    async with get_db_session_context() as db:
        await db.execute(text("UPDATE agn_dependencias SET nombre = 'Alcaldía de Tunja' WHERE codigo = 'ALC'"))
        await db.execute(text("UPDATE agn_dependencias SET nombre = 'Secretaría de Educación' WHERE codigo = 'SECED'"))
        await db.execute(text("UPDATE agn_subseries SET nombre = 'Prestación de Servicios' WHERE codigo = 'PS'"))
        await db.execute(text("UPDATE agn_series SET nombre = 'Contratos' WHERE codigo = 'CON'"))
        await db.commit()
        print("Database encoding fixed.")

if __name__ == '__main__':
    asyncio.run(fix_encoding())
