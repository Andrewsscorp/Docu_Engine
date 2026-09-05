with open("app/routers/documents.py", "r", encoding="utf-8") as f:
    content = f.read()

# We need to add agn_expediente_id to upload_inicial_documento
# async def upload_inicial_documento(
#     request: Request,
#     archivo: UploadFile = File(...),
#     session_data: dict = Depends(require_permission("documentos:subir")),
#     db: AsyncSession = Depends(get_db_session)
# ):

old_def = """async def upload_inicial_documento(
    request: Request,
    archivo: UploadFile = File(...),
    session_data: dict = Depends(require_permission("documentos:subir")),
    db: AsyncSession = Depends(get_db_session)
):"""

new_def = """async def upload_inicial_documento(
    request: Request,
    archivo: UploadFile = File(...),
    agn_expediente_id: str = Form(None),
    session_data: dict = Depends(require_permission("documentos:subir")),
    db: AsyncSession = Depends(get_db_session)
):"""

content = content.replace(old_def, new_def)

# Find the INSERT query and update it
old_query = """INSERT INTO documents (id, tenant_id, group_id, file_name, file_path, uploaded_by, status, is_private, mime_type, file_size_bytes, file_hash, thumbnail_path, extracted_text)
        VALUES (:id, :t, :gid, :fn, :path, :uid, 'PENDING', FALSE, :mime, :size, :hash, :thumb, :text)"""

new_query = """INSERT INTO documents (id, tenant_id, group_id, file_name, file_path, uploaded_by, status, is_private, mime_type, file_size_bytes, file_hash, thumbnail_path, extracted_text, agn_expediente_id)
        VALUES (:id, :t, :gid, :fn, :path, :uid, 'PENDING', FALSE, :mime, :size, :hash, :thumb, :text, :exp_id)"""

content = content.replace(old_query, new_query)

# Add it to the parameter dict
old_params = """"text": fast_route_text
        })"""

new_params = """"text": fast_route_text,
            "exp_id": agn_expediente_id if agn_expediente_id else None
        })"""

content = content.replace(old_params, new_params)

with open("app/routers/documents.py", "w", encoding="utf-8") as f:
    f.write(content)
