with open("app/routers/documents.py", "r", encoding="utf-8") as f:
    content = f.read()

old_sig = """async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    file_hash: str = Form(...),
    group_id: str = Form(None),"""

new_sig = """async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    file_hash: str = Form(None),
    group_id: str = Form(None),"""

content = content.replace(old_sig, new_sig)

old_hash_logic = """    file_content = await file.read()"""
new_hash_logic = """    file_content = await file.read()
    if not file_hash:
        import hashlib
        file_hash = hashlib.sha256(file_content).hexdigest()"""

content = content.replace(old_hash_logic, new_hash_logic)

with open("app/routers/documents.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated upload_document to make file_hash optional")
