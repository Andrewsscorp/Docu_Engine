with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('JSONResponse({"error": "El documento ya existe', 'JSONResponse({"detail": "El documento ya existe')

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated agn.py")
