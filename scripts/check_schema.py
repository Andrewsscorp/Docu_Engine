import asyncio
from sqlalchemy import text
from dotenv import load_dotenv
load_dotenv()
from app.database import AsyncSessionLocal

async def check_schema():
    async with AsyncSessionLocal() as session:
        for t in ["agn_dependencias", "agn_series", "agn_subseries", "agn_expedientes"]:
            print(f"--- {t} ---")
            res = await session.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name='{t}'"))
            for r in res.fetchall():
                print(r.column_name)

if __name__ == "__main__":
    asyncio.run(check_schema())
