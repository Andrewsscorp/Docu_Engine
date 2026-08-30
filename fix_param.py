with open("app/routers/documents.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

# We specifically want to change `archivo: UploadFile` to `file: UploadFile` in upload_inicial_documento
old_sig = """async def upload_inicial_documento(
    request: Request,
    archivo: UploadFile = File(...),"""

new_sig = """async def upload_inicial_documento(
    request: Request,
    file: UploadFile = File(...),"""

content = content.replace(old_sig, new_sig)

# Inside upload_inicial_documento, change archivo to file
# We will just replace it within that function block using a naive string replace
# But let's be safe and just replace exactly the lines we saw.
content = content.replace("safe_name = secure_filename(archivo.filename)", "safe_name = secure_filename(file.filename)")
content = content.replace("content = await archivo.read()", "content = await file.read()")
content = content.replace('mime = archivo.content_type or "application/octet-stream"', 'mime = file.content_type or "application/octet-stream"')

with open("app/routers/documents.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed variable name")
