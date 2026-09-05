import re

# 1. FIX AGN.PY
with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    agn = f.read()

# TRD Delete 1
agn = agn.replace(
    'WHERE expediente_id = :eid AND tipologia_id = :tid\n    \''')',
    'WHERE expediente_id = :eid AND tipologia_id = :tid\n        AND expediente_id IN (SELECT id FROM agn_expedientes WHERE tenant_id = :t)\n    \'\''')'
).replace(
    '{"eid": expediente_id, "tid": tipologia_id})',
    '{"eid": expediente_id, "tid": tipologia_id, "t": session_data["tenant_id"]})'
)

# TRD Delete 2
agn = agn.replace(
    'WHERE expediente_id = :eid\n    \''')',
    'WHERE expediente_id = :eid\n        AND expediente_id IN (SELECT id FROM agn_expedientes WHERE tenant_id = :t)\n    \'\''')'
).replace(
    '{"eid": expediente_id})',
    '{"eid": expediente_id, "t": session_data["tenant_id"]})'
)

# Update Expediente
agn = agn.replace(
    'UPDATE agn_expedientes SET nombre_expediente = :n, soporte = :s WHERE id = :id',
    'UPDATE agn_expedientes SET nombre_expediente = :n, soporte = :s WHERE id = :id AND tenant_id = :t'
).replace(
    '{"n": nombre, "s": soporte, "id": id}',
    '{"n": nombre, "s": soporte, "id": id, "t": session_data["tenant_id"]}'
)
agn = agn.replace(
    'UPDATE agn_expedientes SET nombre_expediente = :n WHERE id = :id',
    'UPDATE agn_expedientes SET nombre_expediente = :n WHERE id = :id AND tenant_id = :t'
).replace(
    '{"n": nombre, "id": id}',
    '{"n": nombre, "id": id, "t": session_data["tenant_id"]}'
)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(agn)

# 2. FIX DOCUMENTS.PY
with open("app/routers/documents.py", "r", encoding="utf-8") as f:
    doc = f.read()

# Download count
doc = doc.replace(
    'UPDATE documents SET download_count = COALESCE(download_count, 0) + 1 WHERE id = :id',
    'UPDATE documents SET download_count = COALESCE(download_count, 0) + 1 WHERE id = :id AND tenant_id = :t'
).replace(
    'await db.execute(update_query, {"id": doc_id})',
    'await db.execute(update_query, {"id": doc_id, "t": session_data["tenant_id"]})'
)

# Assign doc
doc = doc.replace(
    'UPDATE documents SET assigned_user_id = :uid WHERE id = :did",\n            {"uid": asignado_a, "did": doc_id}',
    'UPDATE documents SET assigned_user_id = :uid WHERE id = :did AND tenant_id = :t",\n            {"uid": asignado_a, "did": doc_id, "t": session_data["tenant_id"]}'
)

# OCR
doc = doc.replace('async def iniciar_extraccion_ocr(document_id: str):', 'async def iniciar_extraccion_ocr(document_id: str, tenant_id: str):')
doc = doc.replace(
    'WHERE id = :id"), {"id": document_id}',
    'WHERE id = :id AND tenant_id = :t"), {"id": document_id, "t": tenant_id}'
)
doc = doc.replace('add_task(iniciar_extraccion_ocr, new_doc_id)', 'add_task(iniciar_extraccion_ocr, new_doc_id, session_data["tenant_id"])')
doc = doc.replace('add_task(iniciar_extraccion_ocr, document_id)', 'add_task(iniciar_extraccion_ocr, document_id, session_data["tenant_id"])')
doc = doc.replace('add_task(iniciar_extraccion_ocr, doc_id)', 'add_task(iniciar_extraccion_ocr, doc_id, session_data["tenant_id"])')

with open("app/routers/documents.py", "w", encoding="utf-8") as f:
    f.write(doc)
print("Done!")
