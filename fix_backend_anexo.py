with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

old = """    file_hash = hashlib.sha256(file_content).hexdigest()
    
    disk_filename = f"{file_hash}_{file.filename}"
    file_path = os.path.join(upload_dir, disk_filename)"""

new = """    file_hash = hashlib.sha256(file_content).hexdigest()
    
    disk_filename = f"{file_hash}_{file.filename}"
    file_path = os.path.join(upload_dir, disk_filename)
    
    if tipologia_id == "ANEXO":
        tipologia_id = None"""

content = content.replace(old, new)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
