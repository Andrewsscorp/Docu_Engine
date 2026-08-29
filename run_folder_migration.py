import asyncio
from sqlalchemy import text
from app.database import engine

async def run_migration():
    async with engine.begin() as conn:
        with open('011_folders_and_audit.sql', 'r') as f:
            sql = f.read()
        await conn.execute(text(sql))
        print("Migration executed successfully.")

asyncio.run(run_migration())
