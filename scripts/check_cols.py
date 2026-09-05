import asyncio
from sqlalchemy import text
from dotenv import load_dotenv
load_dotenv()
from app.database import AsyncSessionLocal

async def check():
    async with AsyncSessionLocal() as session:
        res = await session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='documents'"))
        cols = [r[0] for r in res.fetchall()]
        print("Documents cols:", cols)

if __name__ == "__main__":
    asyncio.run(check())
