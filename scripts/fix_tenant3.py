with open("app/routers/documents.py", "r", encoding="utf-8") as f:
    doc = f.read()

doc = doc.replace(
    'await db.execute(text("DELETE FROM documento_etiquetas WHERE id_documento = :did"), {"did": doc_id})',
    'await db.execute(text("DELETE FROM documento_etiquetas WHERE id_documento = :did AND id_documento IN (SELECT id FROM documents WHERE tenant_id = :t)"), {"did": doc_id, "t": session_data["tenant_id"]})'
)
with open("app/routers/documents.py", "w", encoding="utf-8") as f:
    f.write(doc)
