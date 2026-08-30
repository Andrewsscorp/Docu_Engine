with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
# Fix agn.py
old_agn = 'file_path = os.path.join(upload_dir, disk_filename)'
new_agn = 'file_path = os.path.join(upload_dir, disk_filename).replace("\\\\", "/")'
content = content.replace(old_agn, new_agn)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)

with open("app/routers/documents.py", "r", encoding="utf-8") as f:
    content2 = f.read()

old_docs = 'file_path = os.path.join(upload_dir, f"{file_hash}_{file.filename}")'
new_docs = 'file_path = os.path.join(upload_dir, f"{file_hash}_{file.filename}").replace("\\\\", "/")'
content2 = content2.replace(old_docs, new_docs)

with open("app/routers/documents.py", "w", encoding="utf-8") as f:
    f.write(content2)
