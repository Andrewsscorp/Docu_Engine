import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        # Update paths to forward slashes and reset status to PENDING for FAILED docs
        res = await db.execute(text("SELECT id, file_path FROM documents WHERE file_path LIKE '%\\%'"))
        rows = res.fetchall()
        for row in rows:
            new_path = row.file_path.replace("\\", "/")
            await db.execute(text("UPDATE documents SET file_path = :np, status = 'PENDING' WHERE id = :id"), {"np": new_path, "id": row.id})
            print(f"Fixed path for {row.id} to {new_path}")
        await db.commit()

asyncio.run(main())
