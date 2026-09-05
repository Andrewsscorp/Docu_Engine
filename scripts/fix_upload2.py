import re

with open("app/routers/documents.py", "r", encoding="utf-8") as f:
    doc = f.read()

pattern_doc = r"(async def upload_document\([\s\S]*?\):\n[\s\S]*?user_id = session_data\[\"user_id\"\]\n\s+)(from app import rbac)"
replacement_doc = r"""\1
    if file.content_type not in ALLOWED_MIMES:
        raise HTTPException(status_code=400, detail=f"Formato no permitido: {file.content_type}")
        
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="El archivo supera el limite de 50MB.")
        
    \2"""
doc = re.sub(pattern_doc, replacement_doc, doc)

with open("app/routers/documents.py", "w", encoding="utf-8") as f:
    f.write(doc)
