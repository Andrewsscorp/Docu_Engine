with open("app/routers/documents.py", "r", encoding="utf-8") as f:
    content = f.read()

old_func = """async def upload_inicial_documento(
    request: Request,
    archivo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session),
    session_data: dict = Depends(require_permission("documentos:subir"))
):"""

new_func = """async def upload_inicial_documento(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session),
    session_data: dict = Depends(require_permission("documentos:subir"))
):"""

content = content.replace(old_func, new_func)

# We also need to change references to `archivo` inside the function to `file`.
# Let's see how `archivo` is used.
