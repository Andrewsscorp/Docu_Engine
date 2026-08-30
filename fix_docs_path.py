with open("app/routers/documents.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
pattern_docs = r'("score": 1\.0 if final_status == "COMPLETED" else None,\s*"path": )file_path(,\s*"thumb": thumbnail_path,)'
content = re.sub(pattern_docs, r'\1f"{file_hash}_{file.filename}"\2', content)

with open("app/routers/documents.py", "w", encoding="utf-8") as f:
    f.write(content)
print("documents.py updated")
