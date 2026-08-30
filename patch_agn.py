with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

old_func = """async def post_upload_direct_expediente(
    expediente_id: str,
    tipologia_id: str = Form(...),
    file: UploadFile = File(...),
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    import os
    import hashlib
    import fitz
    
    tenant_id = session_data["tenant_id"]
    upload_dir = os.path.join("uploads", str(tenant_id))
    os.makedirs(upload_dir, exist_ok=True)
    
    file_content = await file.read()
    file_hash = hashlib.sha256(file_content).hexdigest()
    
    disk_filename = f"{file_hash}_{file.filename}"
    file_path = os.path.join(upload_dir, disk_filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)
        
    pages = 1
    if file_path.lower().endswith('.pdf'):
        try:
            doc_pdf = fitz.open(file_path)
            pages = doc_pdf.page_count
        except:
            pass
            
    res_doc = await db.execute(text(\'\'\'
        INSERT INTO documents (tenant_id, file_name, file_path, uploaded_by, status, is_private, mime_type, file_size_bytes, file_hash, agn_expediente_id, tipologia_id, paginas_cantidad)
        VALUES (:t, :n, :p, :u, 'COMPLETED', FALSE, :m, :s, :h, :eid, :tid, :pages)
        RETURNING id
    \'\'\'), {
        "t": tenant_id, "n": file.filename, "p": file_path, "u": session_data["user_id"],
        "m": file.content_type, "s": len(file_content), "h": file_hash, "eid": expediente_id, "tid": tipologia_id,
        "pages": pages
    })
    
    new_doc_id = str(res_doc.scalar())
    
    # Índice Electrónico
    index_seed = f"{expediente_id}|{new_doc_id}|{session_data['user_id']}"
    new_index_hash = hashlib.sha256(index_seed.encode()).hexdigest()
    
    await db.execute(text(\'\'\'
        INSERT INTO agn_indice_electronico (expediente_id, documento_id, accion, usuario_id, firma_indice)
        VALUES (:eid, :did, 'VINCULAR_DOCUMENTO', :uid, :ihash)
    \'\'\'), {
        "eid": expediente_id, "did": new_doc_id, "uid": session_data["user_id"], "ihash": new_index_hash
    })
    
    await db.commit()
    
    return JSONResponse({"status": "success"})"""

new_func = """async def post_upload_direct_expediente(
    expediente_id: str,
    background_tasks: BackgroundTasks,
    tipologia_id: str = Form(...),
    file: UploadFile = File(...),
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    import os
    import hashlib
    import fitz
    from app.routers.documents import iniciar_extraccion_ocr
    
    tenant_id = session_data["tenant_id"]
    upload_dir = os.path.join("uploads", str(tenant_id))
    os.makedirs(upload_dir, exist_ok=True)
    
    file_content = await file.read()
    file_hash = hashlib.sha256(file_content).hexdigest()
    
    disk_filename = f"{file_hash}_{file.filename}"
    file_path = os.path.join(upload_dir, disk_filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)
        
    pages = 1
    if file_path.lower().endswith('.pdf'):
        try:
            doc_pdf = fitz.open(file_path)
            pages = doc_pdf.page_count
        except:
            pass
            
    res_doc = await db.execute(text(\'\'\'
        INSERT INTO documents (tenant_id, file_name, file_path, uploaded_by, status, is_private, mime_type, file_size_bytes, file_hash, agn_expediente_id, tipologia_id, paginas_cantidad)
        VALUES (:t, :n, :p, :u, 'PENDING', FALSE, :m, :s, :h, :eid, :tid, :pages)
        RETURNING id
    \'\'\'), {
        "t": tenant_id, "n": file.filename, "p": file_path, "u": session_data["user_id"],
        "m": file.content_type, "s": len(file_content), "h": file_hash, "eid": expediente_id, "tid": tipologia_id,
        "pages": pages
    })
    
    new_doc_id = str(res_doc.scalar())
    
    # Índice Electrónico
    index_seed = f"{expediente_id}|{new_doc_id}|{session_data['user_id']}"
    new_index_hash = hashlib.sha256(index_seed.encode()).hexdigest()
    
    await db.execute(text(\'\'\'
        INSERT INTO agn_indice_electronico (expediente_id, documento_id, accion, usuario_id, firma_indice)
        VALUES (:eid, :did, 'VINCULAR_DOCUMENTO', :uid, :ihash)
    \'\'\'), {
        "eid": expediente_id, "did": new_doc_id, "uid": session_data["user_id"], "ihash": new_index_hash
    })
    
    background_tasks.add_task(iniciar_extraccion_ocr, new_doc_id)
    
    await db.commit()
    
    return JSONResponse({"status": "success"})"""

# There are some garbage characters in the old func text ""oǪndice Electr"o"'nico", let's use regex to replace it
import re

pattern = re.compile(r'async def post_upload_direct_expediente.*?return JSONResponse\(\{"status": "success"\}\)', re.DOTALL)
content = pattern.sub(new_func, content)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
