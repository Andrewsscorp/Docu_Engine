import re

with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

# We need to wrap the execute block in try/except IntegrityError
old_block = """    res_doc = await db.execute(text('''
        INSERT INTO documents (tenant_id, file_name, file_path, uploaded_by, status, is_private, mime_type, file_size_bytes, file_hash, agn_expediente_id, tipologia_id, paginas_cantidad, thumbnail_path)
        VALUES (:t, :n, :p, :u, 'PENDING', FALSE, :m, :s, :h, :eid, :tid, :pages, :thumb)
        RETURNING id
    '''), {
        "t": tenant_id, "n": file.filename, "p": disk_filename, "u": session_data["user_id"],
        "m": file.content_type, "s": len(file_content), "h": file_hash, "eid": expediente_id, "tid": tipologia_id,
        "pages": pages, "thumb": thumbnail_path
    })
    
    new_doc_id = str(res_doc.scalar())"""

new_block = """    from sqlalchemy.exc import IntegrityError
    try:
        res_doc = await db.execute(text('''
            INSERT INTO documents (tenant_id, file_name, file_path, uploaded_by, status, is_private, mime_type, file_size_bytes, file_hash, agn_expediente_id, tipologia_id, paginas_cantidad, thumbnail_path)
            VALUES (:t, :n, :p, :u, 'PENDING', FALSE, :m, :s, :h, :eid, :tid, :pages, :thumb)
            RETURNING id
        '''), {
            "t": tenant_id, "n": file.filename, "p": disk_filename, "u": session_data["user_id"],
            "m": file.content_type, "s": len(file_content), "h": file_hash, "eid": expediente_id, "tid": tipologia_id,
            "pages": pages, "thumb": thumbnail_path
        })
        new_doc_id = str(res_doc.scalar())
    except IntegrityError:
        await db.rollback()
        return JSONResponse({"error": "El documento ya existe en el sistema (Hash duplicado)."}, status_code=409)"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open("app/routers/agn.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Success")
else:
    print("Block not found!")
