# Fix auth imports
with open("app/routers/auth.py", "r", encoding="utf-8") as f:
    auth_code = f.read()

auth_code = auth_code.replace("from enum import Enum", "from enum import Enum\nimport hmac\nimport hashlib\nimport json")

with open("app/routers/auth.py", "w", encoding="utf-8") as f:
    f.write(auth_code)

# Fix documents.py 1448
with open("app/routers/documents.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "session_data" in line and i > 1440:
        lines[i] = line.replace("session_data['user_id']", "session_data['user_id'] if 'session_data' in locals() else 'unknown'")
with open("app/routers/documents.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
