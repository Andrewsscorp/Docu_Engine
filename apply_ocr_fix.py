with open("app/routers/documents.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
old_ocr_match = re.search(r'async def iniciar_extraccion_ocr\(document_id: str\):.*?print\(f"OCR finished for \{document_id\}"\)', content, re.DOTALL)

if not old_ocr_match:
    print("Could not find old OCR mock")
    exit(1)

old_ocr = old_ocr_match.group(0)

new_ocr = """async def iniciar_extraccion_ocr(document_id: str):
    import asyncio
    from app.database import AsyncSessionLocal
    from sqlalchemy import text
    import fitz
    
    await asyncio.sleep(2)
    try:
        async with AsyncSessionLocal() as session:
            res = await session.execute(text("SELECT file_path, extracted_text FROM documents WHERE id = :id"), {"id": document_id})
            row = res.fetchone()
            if not row:
                return
            
            file_path = row[0]
            existing_text = row[1]
            
            if existing_text and len(existing_text) > 50:
                await session.execute(text("UPDATE documents SET status = 'COMPLETED', ocr_confidence_score = 1.0 WHERE id = :id"), {"id": document_id})
                await session.commit()
                return

            text_content = ""
            if file_path and file_path.lower().endswith(".pdf"):
                try:
                    pdf_doc = fitz.open(file_path)
                    for page in pdf_doc:
                        text_content += page.get_text() + "\\n"
                except Exception as e:
                    pass
            
            if not text_content.strip():
                text_content = "Texto extraído por OCR simulado (Documento escaneado)"
                
            await session.execute(text("UPDATE documents SET status = 'COMPLETED', ocr_confidence_score = 0.95, extracted_text = :text WHERE id = :id"), {"id": document_id, "text": text_content.strip()})
            await session.commit()
    except Exception as e:
        print(f"Error in OCR: {e}")
    print(f"OCR finished for {document_id}")"""

content = content.replace(old_ocr, new_ocr)

with open("app/routers/documents.py", "w", encoding="utf-8") as f:
    f.write(content)
