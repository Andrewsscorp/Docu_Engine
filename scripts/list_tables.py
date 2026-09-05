import asyncio
from sqlalchemy import text
from dotenv import load_dotenv
load_dotenv()
from app.database import AsyncSessionLocal

async def list_tables():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        for row in result.fetchall():
            print(row.table_name)

if __name__ == "__main__":
    asyncio.run(list_tables())
