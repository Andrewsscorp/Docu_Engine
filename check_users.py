import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://postgres:superadmin_password@localhost:5432/docuengine"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def main():
    async with async_session() as session:
        res = await session.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users'"))
        for row in res.fetchall():
            print(f"{row[0]}: {row[1]}")

asyncio.run(main())
