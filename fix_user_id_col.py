with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("doc.user_id as autor_carga", "doc.uploaded_by as autor_carga")

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
