import asyncio
from sqlalchemy import text
from dotenv import load_dotenv
load_dotenv()
from app.database import AsyncSessionLocal

async def check():
    async with AsyncSessionLocal() as session:
        for t in ["documents", "roles", "groups"]:
            res = await session.execute(text(f"SELECT tenant_id FROM {t} LIMIT 1"))
            row = res.fetchone()
            if row:
                print(f"{t}: {row.tenant_id}")

if __name__ == "__main__":
    asyncio.run(check())
