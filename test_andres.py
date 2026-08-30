import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def test():
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("SELECT r.name FROM users u JOIN roles r ON u.role_id = r.id WHERE u.username = 'andres'"))
        print(f"Role of andres: {res.fetchone()[0]}")

asyncio.run(test())
