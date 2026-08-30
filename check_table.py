import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        try:
            res = await db.execute(text("SELECT * FROM tenant_ocr_settings"))
            print("Table exists!")
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(main())
