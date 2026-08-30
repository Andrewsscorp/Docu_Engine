import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        # Set all PENDING back to COMPLETED except the two newest
        res = await db.execute(text("UPDATE documents SET status = 'COMPLETED' WHERE status = 'PENDING' AND id NOT IN ('0f00adc1-b624-451b-8a52-31f617733e41', '93318f97-809d-43a6-800a-c135a88eae64')"))
        await db.commit()
        print("Updated older documents to COMPLETED.")

asyncio.run(main())
