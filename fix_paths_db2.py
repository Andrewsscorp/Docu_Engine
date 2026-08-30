import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        res = await db.execute(text("SELECT id, file_path FROM documents WHERE status = 'FAILED'"))
        rows = res.fetchall()
        for row in rows:
            new_path = row.file_path.replace("\\", "/")
            await db.execute(text("UPDATE documents SET file_path = :np, status = 'PENDING' WHERE id = :id"), {"np": new_path, "id": row.id})
            print(f"Fixed {row.id} -> {new_path}")
        await db.commit()

asyncio.run(main())
