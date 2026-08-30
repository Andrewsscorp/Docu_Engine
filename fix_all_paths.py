import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        # Select all that contain a slash or backslash
        res = await db.execute(text("SELECT id, file_path FROM documents WHERE file_path LIKE '%/%' OR file_path LIKE '%\\%'"))
        rows = res.fetchall()
        for row in rows:
            # Extract just the filename
            filename = row.file_path.replace("\\", "/").split("/")[-1]
            await db.execute(text("UPDATE documents SET file_path = :fn, status = 'PENDING' WHERE id = :id"), {"fn": filename, "id": row.id})
            print(f"Fixed {row.id} -> {filename}")
        await db.commit()

asyncio.run(main())
