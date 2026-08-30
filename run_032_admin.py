import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def run():
    engine = create_async_engine("postgresql+asyncpg://postgres:superadmin_password@localhost:5432/docuengine")
    async with engine.begin() as conn:
        with open("032_inmutabilidad_fuid.sql", "r", encoding="utf-8") as f:
            sql = f.read().lstrip("\ufeff")
            
        statements = []
        current = []
        for line in sql.split("\n"):
            current.append(line)
            if line.strip().endswith(";") and not ("$$" in "\n".join(current) and current[-1].strip() != "$$ LANGUAGE plpgsql;"):
                statements.append("\n".join(current))
                current = []
        
        if current and "".join(current).strip():
            statements.append("\n".join(current))
            
        for stmt in statements:
            if stmt.strip():
                await conn.execute(text(stmt))
                
        # Grant privileges just in case
        await conn.execute(text("GRANT ALL PRIVILEGES ON TABLE fuid_transferencias TO docuengine_api;"))
        await conn.execute(text("GRANT ALL PRIVILEGES ON TABLE fuid_expedientes_vinculados TO docuengine_api;"))

asyncio.run(run())
