with open("migrations/005_append_only_audit.sql", "r", encoding="utf-8-sig") as f:
    sql_content = f.read()

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def run():
    engine = create_async_engine("postgresql+asyncpg://docuengine_api:api_secure_password_123@localhost:5432/docuengine")
    
    # asyncpg doesn't support executing multiple statements separated by semicolon inside a single text() block easily.
    # We should split by ';' and execute them individually.
    
    statements = sql_content.split(';')
    
    async with engine.begin() as conn:
        for stmt in statements:
            if stmt.strip():
                if "CREATE OR REPLACE FUNCTION" in stmt:
                    # Functions have internal semicolons inside $$, don't split those easily.
                    pass
        
        # Actually it's better to use raw connection or execute the whole block if dialect supports it.
        # But wait, asyncpg text() CAN execute multiple statements if we just don't use text() but raw await conn.execute() 
        # However SQLAlchemy text() executes only the first one or raises an error if multiple.
        # Let's write a simple python parser for the statements.
        pass

    # A better way is to just use psql or let asyncpg run it via raw connection:
    raw_conn = await engine.raw_connection()
    try:
        # raw_conn is an AsyncAdapt_asyncpg_connection
        await raw_conn._connection.execute(sql_content)
        print("Migration 005 applied successfully!")
    finally:
        await raw_conn.close()
            
asyncio.run(run())
