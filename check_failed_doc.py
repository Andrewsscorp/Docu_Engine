import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        res = await db.execute(text("SELECT status, ocr_confidence_score, extracted_text, file_path FROM documents WHERE id = '0f00adc1-b624-451b-8a52-31f617733e41'"))
        print(res.fetchone())

asyncio.run(main())
