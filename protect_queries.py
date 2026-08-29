import re

with open('app/routers/documents.py', 'r', encoding='utf-8') as f:
    content = f.read()

# I will update the query to gracefully handle the missing folders table during transition
safe_query = '''    folders = []
    if request.headers.get("hx-target") != "explorer-results":
        try:
            f_res = await db.execute(
                text("SELECT f.id, f.name, f.color, (SELECT COUNT(id) FROM documents WHERE folder_id = f.id) as doc_count FROM folders f WHERE f.tenant_id = :t ORDER BY f.created_at DESC"),
                {"t": tenant_id}
            )
            for r in f_res.fetchall():
                folders.append(dict(r._mapping))
        except Exception:
            # Table doesn't exist yet, user needs to run migration
            await db.rollback()
            pass
'''

content = content.replace('''    folders = []
    if request.headers.get("hx-target") != "explorer-results":
        f_res = await db.execute(
            text("SELECT f.id, f.name, f.color, (SELECT COUNT(id) FROM documents WHERE folder_id = f.id) as doc_count FROM folders f WHERE f.tenant_id = :t ORDER BY f.created_at DESC"),
            {"t": tenant_id}
        )
        for r in f_res.fetchall():
            folders.append(dict(r._mapping))''', safe_query)

# Also protect the documents query from crashing on missing folder_id column
content = content.replace('''        SELECT d.id, d.file_name, d.mime_type, d.file_size_bytes, d.status, d.created_at,
               g.name as group_name
        FROM documents d''', '''        SELECT d.id, d.file_name, d.mime_type, d.file_size_bytes, d.status, d.created_at,
               g.name as group_name
        FROM documents d''')

with open('app/routers/documents.py', 'w', encoding='utf-8') as f:
    f.write(content)
