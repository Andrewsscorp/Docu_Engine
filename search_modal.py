with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if "Nuevo Documento" in line or "modal" in line.lower() or "upload" in line.lower():
            pass # this is too broad
