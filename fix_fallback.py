with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

old_docs = """docs = []
    for row in docs_res.fetchall():
        d = dict(row._mapping)
        d["fecha_str"] = d["created_at"].strftime("%Y-%m-%d") if d["created_at"] else ""
        docs.append(d)"""

new_docs = """docs = []
    for row in docs_res.fetchall():
        d = dict(row._mapping)
        d["fecha_str"] = d["created_at"].strftime("%Y-%m-%d") if d["created_at"] else ""
        if not d.get("tipo_nombre"):
            d["tipo_nombre"] = "Archivo Adjunto / Anexo"
        docs.append(d)"""

content = content.replace(old_docs, new_docs)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
