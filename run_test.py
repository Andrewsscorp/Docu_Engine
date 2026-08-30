import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def apply_migration():
    sql = """
    CREATE VIEW vista_test AS SELECT 1 as foo;
    """
    
    async with AsyncSessionLocal() as session:
        await session.execute(text(sql))
        await session.commit()
        print("View created!")

asyncio.run(apply_migration())
