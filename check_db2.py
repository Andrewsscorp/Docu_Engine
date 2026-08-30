import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def get_schema():
    async with AsyncSessionLocal() as session:
        res = await session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        for row in res:
            print(row[0])
            
asyncio.run(get_schema())
