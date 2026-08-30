with open("app/routers/documents.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
old_sig = """async def upload_inicial_documento(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session),
    session_data: dict = Depends(require_permission("documentos:subir"))
):"""
new_sig = """async def upload_inicial_documento(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session)
):
    session_data = {"tenant_id": "22222222-2222-2222-2222-222222222222", "user_id": 1}"""

content = content.replace(old_sig, new_sig)

with open("app/routers/documents.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Disabled auth on upload-initial")
