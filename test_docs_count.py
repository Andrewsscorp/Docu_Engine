import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def test():
    async with AsyncSessionLocal() as db:
        await db.execute(text("SELECT set_config('app.tenant_id', '22222222-2222-2222-2222-222222222222', false)"))
        await db.execute(text("SELECT set_config('app.is_superadmin', 'true', false)"))
        res = await db.execute(text("SELECT count(*) FROM documents"))
        print(f"Count: {res.scalar()}")

asyncio.run(test())
