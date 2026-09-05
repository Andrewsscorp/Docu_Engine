import asyncio
from sqlalchemy import text
from dotenv import load_dotenv
load_dotenv()
from app.database import AsyncSessionLocal

async def check():
    async with AsyncSessionLocal() as session:
        res = await session.execute(text("SELECT id FROM users LIMIT 1"))
        user = res.fetchone()
        if user:
            print("user:", user.id)
        else:
            print("NO USERS")

if __name__ == "__main__":
    asyncio.run(check())
