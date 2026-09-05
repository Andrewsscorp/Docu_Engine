with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    agn = f.read()

import re
match = re.search(r'(async def log_audit_sgdea_async.*?)\n\n', agn, re.DOTALL)
if match:
    print(match.group(1))
