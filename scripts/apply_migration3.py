import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
import asyncpg

async def run():
    with open("migrations/005_append_only_audit.sql", "r", encoding="utf-8-sig") as f:
        sql_content = f.read()
    
    # Try connecting as postgres user
    try:
        conn = await asyncpg.connect("postgresql://postgres:postgres@localhost:5432/docuengine")
        await conn.execute(sql_content)
        print("Migration 005 applied successfully as postgres!")
        await conn.close()
    except Exception as e:
        print(f"Error as postgres: {e}")
            
asyncio.run(run())
