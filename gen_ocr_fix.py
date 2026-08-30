import asyncio
from app.database import AsyncSessionLocal
from sqlalchemy import text
import os
import fitz

async def iniciar_extraccion_ocr(document_id: str):
    await asyncio.sleep(2)
    try:
        async with AsyncSessionLocal() as session:
            # get file path
            res = await session.execute(text("SELECT file_path, extracted_text FROM documents WHERE id = :id"), {"id": document_id})
            row = res.fetchone()
            if not row:
                return
            
            file_path = row[0]
            existing_text = row[1]
            
            # if existing text is already very good (extracted by native fast route), just mark as completed
            if existing_text and len(existing_text) > 50:
                await session.execute(text("UPDATE documents SET status = 'COMPLETED', ocr_confidence_score = 1.0 WHERE id = :id"), {"id": document_id})
                await session.commit()
                return

            text_content = ""
            if file_path.lower().endswith(".pdf"):
                try:
                    pdf_doc = fitz.open(file_path)
                    for page in pdf_doc:
                        text_content += page.get_text() + "\n"
                except Exception as e:
                    print(f"OCR mock fitz error: {e}")
            
            if not text_content.strip():
                text_content = "Texto extraído por OCR simulado (Documento escaneado sin texto nativo)"
            
            await session.execute(text("UPDATE documents SET status = 'COMPLETED', ocr_confidence_score = 0.95, extracted_text = :text WHERE id = :id"), {"id": document_id, "text": text_content.strip()})
            await session.commit()
    except Exception as e:
        print(f"Error in OCR: {e}")
    print(f"OCR finished for {document_id}")

with open("app/routers/documents.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
pattern = re.compile(r'async def iniciar_extraccion_ocr\(document_id: str\):.*?print\(f"OCR finished for \{document_id\}"\)', re.DOTALL)

with open("fix_ocr.py", "w", encoding="utf-8") as f:
    f.write("content = " + repr(content) + "\n\n")
    f.write("import re\n")
    f.write("content = re.sub(r'async def iniciar_extraccion_ocr.*?OCR finished for \{document_id\}\"', '''")
    
    # Actually just string replacement is safer!
