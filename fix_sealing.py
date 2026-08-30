with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

# Add validation for 0 documents
old_check = """    for rid in req_ids:
        if rid not in doc_tipos:
            raise HTTPException(status_code=403, detail="El expediente no cumple el 100% de la completitud documental. Faltan tipologías obligatorias.")"""

new_check = """    if len(docs) == 0:
        raise HTTPException(status_code=403, detail="Un expediente vacío (0 documentos) no puede ser cerrado o transferido. Debe contener al menos un documento.")
        
    for rid in req_ids:
        if rid not in doc_tipos:
            raise HTTPException(status_code=403, detail="El expediente no cumple el 100% de la completitud documental. Faltan tipologías obligatorias.")"""

content = content.replace(old_check, new_check)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated backend sealing validation")
