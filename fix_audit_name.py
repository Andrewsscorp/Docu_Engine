with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("EXPORTACION_METADATOS_PLANA", "DESCARGA_METADATOS_PLANA")

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
