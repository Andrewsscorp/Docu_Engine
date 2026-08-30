import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()

async def run():
    import sys
    sys.path.append(".")
    from app.database import DATABASE_URL
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        with open("032_inmutabilidad_fuid.sql", "r", encoding="utf-8") as f:
            sql = f.read().lstrip("\ufeff")
            
        # Very simple splitting logic
        statements = []
        current = []
        for line in sql.split("\n"):
            current.append(line)
            # if we see end of function or a normal semicolon that is not in a function
            if line.strip().endswith(";") and not ("$$" in "\n".join(current) and current[-1].strip() != "$$ LANGUAGE plpgsql;"):
                statements.append("\n".join(current))
                current = []
        
        if current and "".join(current).strip():
            statements.append("\n".join(current))
            
        for stmt in statements:
            if stmt.strip():
                await conn.execute(text(stmt))

asyncio.run(run())
