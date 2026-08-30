with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

old_return = """    return JSONResponse([{"id": str(t["id"]), "text": f"[{t['codigo_tipologia']}] {t['nombre']}"} for t in tipologias])"""
new_return = """    return JSONResponse([{"id": str(t["id"]), "text": f"[{t['codigo_tipologia']}] {t['nombre']}" if t['codigo_tipologia'] else t['nombre']} for t in tipologias])"""

content = content.replace(old_return, new_return)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
