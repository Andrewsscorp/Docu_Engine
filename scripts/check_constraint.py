import asyncio
from sqlalchemy import text
from dotenv import load_dotenv
load_dotenv()
from app.database import AsyncSessionLocal

async def check():
    async with AsyncSessionLocal() as session:
        res = await session.execute(text("SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname = 'agn_dependencias_tipo_check'"))
        print(res.fetchone()[0])

if __name__ == "__main__":
    asyncio.run(check())
