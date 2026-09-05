import os

with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    agn_content = f.read()

# Fix DELETE FROM agn_expediente_tipologia WHERE expediente_id = :eid AND tipologia_id = :tid
agn_content = agn_content.replace(
    """DELETE FROM agn_expediente_tipologia 
        WHERE expediente_id = :eid AND tipologia_id = :tid""",
    """DELETE FROM agn_expediente_tipologia 
        WHERE expediente_id = :eid AND tipologia_id = :tid 
        AND expediente_id IN (SELECT id FROM agn_expedientes WHERE tenant_id = :t)"""
)

# Fix DELETE FROM agn_expediente_tipologia WHERE expediente_id = :eid
agn_content = agn_content.replace(
    """DELETE FROM agn_expediente_tipologia 
        WHERE expediente_id = :eid""",
    """DELETE FROM agn_expediente_tipologia 
        WHERE expediente_id = :eid 
        AND expediente_id IN (SELECT id FROM agn_expedientes WHERE tenant_id = :t)"""
)

# Need to update the parameter passing to include :t
agn_content = agn_content.replace(
    '{"eid": expediente_id, "tid": tipologia_id})',
    '{"eid": expediente_id, "tid": tipologia_id, "t": session_data["tenant_id"]})'
)
agn_content = agn_content.replace(
    '{"eid": expediente_id})',
    '{"eid": expediente_id, "t": session_data["tenant_id"]})'
)


# Fix UPDATE agn_expedientes SET nombre_expediente
agn_content = agn_content.replace(
    'UPDATE agn_expedientes SET nombre_expediente = :n, soporte = :s WHERE id = :id',
    'UPDATE agn_expedientes SET nombre_expediente = :n, soporte = :s WHERE id = :id AND tenant_id = :t'
)
agn_content = agn_content.replace(
    'UPDATE agn_expedientes SET nombre_expediente = :n WHERE id = :id',
    'UPDATE agn_expedientes SET nombre_expediente = :n WHERE id = :id AND tenant_id = :t'
)
agn_content = agn_content.replace(
    '{"n": nombre, "s": soporte, "id": id}',
    '{"n": nombre, "s": soporte, "id": id, "t": session_data["tenant_id"]}'
)
agn_content = agn_content.replace(
    '{"n": nombre, "id": id}',
    '{"n": nombre, "id": id, "t": session_data["tenant_id"]}'
)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(agn_content)


with open("app/routers/documents.py", "r", encoding="utf-8") as f:
    doc_content = f.read()

doc_content = doc_content.replace(
    "UPDATE documents SET download_count = COALESCE(download_count, 0) + 1 WHERE id = :id",
    "UPDATE documents SET download_count = COALESCE(download_count, 0) + 1 WHERE id = :id AND tenant_id = :t"
)
doc_content = doc_content.replace(
    '{"id": document_id}',
    '{"id": document_id, "t": session_data["tenant_id"]}'
)

# Fix Reassign User
doc_content = doc_content.replace(
    "UPDATE documents SET assigned_user_id = :uid WHERE id = :did",
    "UPDATE documents SET assigned_user_id = :uid WHERE id = :did AND tenant_id = :t"
)
doc_content = doc_content.replace(
    '{"uid": user_id, "did": document_id}',
    '{"uid": user_id, "did": document_id, "t": session_data["tenant_id"]}'
)

# Fix OCR Update (Wait, OCR background task doesn't have session_data easily accessible, let's look at it closer first)
with open("app/routers/documents.py", "w", encoding="utf-8") as f:
    f.write(doc_content)

print("Basic fixes applied. Needs careful manual review.")
