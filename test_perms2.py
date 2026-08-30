import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def test():
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("""
            SELECT p.name 
            FROM role_permissions rp
            JOIN permissions p ON rp.permission_id = p.id
            JOIN users u ON u.role_id = rp.role_id
            WHERE u.username = 'andres'
        """))
        perms = [r[0] for r in res.fetchall()]
        print(f"Permisos de andres: {perms}")

asyncio.run(test())
