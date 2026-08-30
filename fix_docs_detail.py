with open("app/routers/documents.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('JSONResponse({"error": "Archivo ya procesado', 'JSONResponse({"detail": "Archivo ya procesado')

with open("app/routers/documents.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated documents.py")
