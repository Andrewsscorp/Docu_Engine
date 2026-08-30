import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        await db.execute(text("UPDATE documents SET status = 'COMPLETED' WHERE id = 'c3afcaf1-9e6d-46d4-a331-75217844f768'"))
        await db.commit()
        print("Set stuck document to COMPLETED")

asyncio.run(main())
