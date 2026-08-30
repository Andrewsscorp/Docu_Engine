with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('return JSONResponse({"status": "success"})', 'return JSONResponse({"status": "success", "xml_hash": raw_hash})')

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
