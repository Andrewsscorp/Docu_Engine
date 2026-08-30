with open("app/routers/documents.py", "r", encoding="utf-8") as f:
    content = f.read()

old_ocr = """async def iniciar_extraccion_ocr(document_id: str):
    # This simulates a background task taking time without blocking the main event loop
    await asyncio.sleep(2)
    # Here it would update the DB...
    print(f"OCR finished for {document_id}")"""

new_ocr = """async def iniciar_extraccion_ocr(document_id: str):
    import asyncio
    from app.database import AsyncSessionLocal
    from sqlalchemy import text
    await asyncio.sleep(2)
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("UPDATE documents SET status = 'COMPLETED', ocr_confidence_score = 0.99, extracted_text = 'Texto extraído por OCR simulado' WHERE id = :id"), {"id": document_id})
            await session.commit()
    except Exception as e:
        print(f"Error in OCR: {e}")
    print(f"OCR finished for {document_id}")"""

content = content.replace(old_ocr, new_ocr)

with open("app/routers/documents.py", "w", encoding="utf-8") as f:
    f.write(content)
